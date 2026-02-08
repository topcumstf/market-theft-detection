import csv
import time
from datetime import datetime
from pathlib import Path

import cv2

from PyQt5.QtCore import QTimer, Qt, QSettings
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QSplitter

from app.ui.widgets.video_widget import VideoWidget
from app.ui.widgets.controls_widget import ControlsWidget
from app.ui.widgets.log_panel import LogPanel
from app.ui.widgets.status_panel import StatusPanel
from app.ui.widgets.last_event_panel import LastEventPanel
from app.ui.widgets.metrics_panel import MetricsPanel

from app.services.camera_service import CameraService
from app.services.inference_service import InferenceService
from app.services.tracking_service import TrackingService
from app.services.event_service import EventService
from app.data.db import Database


def project_root() -> Path:
    # app/ui/main_window.py -> ui -> app -> PROJECT_ROOT
    return Path(__file__).resolve().parents[2]


OUT_DIR = project_root() / "outputs"
SNAP_DIR = OUT_DIR / "snapshots"
EXPORT_DIR = OUT_DIR / "exports"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Market Theft Detection - MVP")

        self.settings = QSettings("MarketTheftMVP")

        self.camera = CameraService(camera_index=0)
        self.inferencer = InferenceService("yolov8n.pt", conf=0.45)
        self.tracker = TrackingService()
        self.event_service = EventService(near_required_time=3.0, disappear_time=3.0)
        self.db = Database()

        self.video = VideoWidget()
        self.log_panel = LogPanel()
        self.controls = ControlsWidget()
        self.status_panel = StatusPanel()
        self.metrics_panel = MetricsPanel()
        self.last_event_panel = LastEventPanel()

        self._refresh_cameras(initial=True)

        self._last_frame_ts = None
        self._fps_smooth = 0.0
        self._lat_smooth = 0.0

        self.timer = QTimer(self)
        self.timer.setInterval(30)
        self.timer.timeout.connect(self._tick)

        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QVBoxLayout()
        root.setLayout(root_layout)

        right_splitter = QSplitter(Qt.Vertical)
        right_splitter.addWidget(self.status_panel)
        right_splitter.addWidget(self.metrics_panel)
        right_splitter.addWidget(self.last_event_panel)
        right_splitter.addWidget(self.log_panel)
        right_splitter.setSizes([60, 60, 180, 500])

        top_splitter = QSplitter(Qt.Horizontal)
        top_splitter.addWidget(self.video)
        top_splitter.addWidget(right_splitter)
        top_splitter.setStretchFactor(0, 3)
        top_splitter.setStretchFactor(1, 1)

        bottom_container = QWidget()
        bottom_layout = QVBoxLayout()
        bottom_layout.setContentsMargins(8, 8, 8, 8)
        bottom_layout.setSpacing(8)
        bottom_container.setLayout(bottom_layout)
        bottom_container.setMinimumHeight(170)
        bottom_layout.addWidget(self.controls)

        main_splitter = QSplitter(Qt.Vertical)
        main_splitter.addWidget(top_splitter)
        main_splitter.addWidget(bottom_container)
        main_splitter.setStretchFactor(0, 8)
        main_splitter.setStretchFactor(1, 2)

        root_layout.addWidget(main_splitter)

        self.controls.start_clicked.connect(self.on_start)
        self.controls.stop_clicked.connect(self.on_stop)
        self.controls.refresh_cameras_clicked.connect(lambda: self._refresh_cameras(initial=False))
        self.controls.camera_changed.connect(self.on_camera_changed)

        self.controls.conf_changed.connect(self.on_conf_changed)
        self.controls.near_time_changed.connect(self.on_near_time_changed)
        self.controls.disappear_time_changed.connect(self.on_disappear_time_changed)

        self.controls.export_csv_clicked.connect(self.export_csv)

        self.status_panel.set_running(False)
        self.last_event_panel.set_text("—")
        self.log_panel.log(f"Proje klasörü: {project_root()}")
        self.log_panel.log("Hazır. Start → sistem başlar. Event'ler DB'ye kaydedilir.")

        self._load_settings()

    def _load_settings(self):
        conf = float(self.settings.value("conf", 0.45))
        near_t = float(self.settings.value("near_required_time", 3.0))
        dis_t = float(self.settings.value("disappear_time", 3.0))
        cam = int(self.settings.value("camera_index", 0))

        self.controls.sld_conf.setValue(int(conf * 100))
        self.controls.sld_near.setValue(int(near_t))
        self.controls.sld_dis.setValue(int(dis_t))

        self.camera.set_index(cam)
        self.log_panel.log(f"Ayarlar yüklendi: conf={conf:.2f}, near={near_t:.1f}s, dis={dis_t:.1f}s, cam={cam}")

    def on_conf_changed(self, conf: float):
        self.inferencer.set_conf(conf)
        self.settings.setValue("conf", conf)
        self.log_panel.log(f"Ayar güncellendi: confidence={conf:.2f}")

    def on_near_time_changed(self, t: float):
        self.event_service.set_near_required_time(t)
        self.settings.setValue("near_required_time", t)
        self.log_panel.log(f"Ayar güncellendi: near_required_time={t:.1f}s")

    def on_disappear_time_changed(self, t: float):
        self.event_service.set_disappear_time(t)
        self.settings.setValue("disappear_time", t)
        self.log_panel.log(f"Ayar güncellendi: disappear_time={t:.1f}s")

    def _refresh_cameras(self, initial: bool):
        cams = CameraService.list_available(max_index=6)
        if not cams:
            cams = [0]
        self.controls.set_cameras(cams)

        if initial:
            saved_cam = int(self.settings.value("camera_index", 0))
            if saved_cam in cams:
                self.controls.cmb_camera.setCurrentIndex(cams.index(saved_cam))
                self.camera.set_index(saved_cam)
            else:
                self.camera.set_index(self.controls.selected_camera_index())

        self.log_panel.log(f"Kameralar: {cams}")

    def on_camera_changed(self, cam_index: int):
        self.camera.set_index(cam_index)
        self.settings.setValue("camera_index", cam_index)
        self.log_panel.log(f"Kamera seçildi: {cam_index}")

    def on_start(self):
        try:
            self.camera.set_index(self.controls.selected_camera_index())
            self.camera.start()
            self._last_frame_ts = None
            self.timer.start()
            self.controls.set_running(True)
            self.status_panel.set_running(True)
            self.log_panel.log("Sistem başlatıldı.")
        except Exception as e:
            self.controls.set_running(False)
            self.status_panel.set_running(False)
            self.log_panel.log(f"HATA: {e}")

    def on_stop(self):
        self.timer.stop()
        self.camera.stop()
        self.controls.set_running(False)
        self.status_panel.set_running(False)
        self.log_panel.log("Sistem durduruldu.")

        self.video.setPixmap(QPixmap())
        self.video.setText("Video Preview (Ready to Start)")

    def export_csv(self):
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = EXPORT_DIR / f"events_{ts}.csv"

        rows = self.db.fetch_events(limit=5000)
        rows = list(reversed(rows))

        with out_path.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "timestamp", "bottle_id", "message", "snapshot_path"])
            for r in rows:
                writer.writerow([r["id"], r["timestamp"], r["bottle_id"], r["message"], r.get("snapshot_path", "")])

        self.log_panel.log(f"CSV oluşturuldu: {out_path}")

    @staticmethod
    def _draw_box(frame, bbox, text, color_bgr, thickness=2):
        x1, y1, x2, y2 = [int(v) for v in bbox]
        cv2.rectangle(frame, (x1, y1), (x2, y2), color_bgr, thickness)
        cv2.putText(frame, text, (x1, max(0, y1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_bgr, 2, cv2.LINE_AA)

    def _update_metrics(self, start_ts: float):
        end_ts = time.time()
        latency_ms = (end_ts - start_ts) * 1000.0

        if self._last_frame_ts is None:
            fps = 0.0
        else:
            dt = max(1e-6, (end_ts - self._last_frame_ts))
            fps = 1.0 / dt
        self._last_frame_ts = end_ts

        a = 0.1
        self._fps_smooth = (1 - a) * self._fps_smooth + a * fps
        self._lat_smooth = (1 - a) * self._lat_smooth + a * latency_ms
        self.metrics_panel.set_metrics(self._fps_smooth, self._lat_smooth)

    def _tick(self):
        tick_start = time.time()

        frame = self.camera.read()
        if frame is None:
            return

        results = self.inferencer.track(frame)
        tracked = self.tracker.update(results)

        events = self.event_service.update(tracked)
        armed_ids = self.event_service.get_armed_ids()

        annotated = frame.copy()

        for d in tracked:
            cls_id = d["cls_id"]
            tid = d["track_id"]
            bbox = d["bbox"]

            if cls_id == 0:
                self._draw_box(annotated, bbox, f"person ID {tid}", (0, 255, 0))
            elif cls_id == 39:
                if tid in armed_ids:
                    self._draw_box(annotated, bbox, f"bottle ID {tid} (ARMED)", (0, 0, 255))
                else:
                    self._draw_box(annotated, bbox, f"bottle ID {tid}", (255, 255, 0))

        for ev in events:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            bottle_id = None
            try:
                bottle_id = int(ev.split("ID")[1].split()[0])
            except Exception:
                pass

            SNAP_DIR.mkdir(parents=True, exist_ok=True)
            ts_file = datetime.now().strftime("%Y%m%d_%H%M%S")
            snap_path = SNAP_DIR / f"event_{ts_file}_bottle_{bottle_id}.jpg"

            ok = cv2.imwrite(str(snap_path), annotated)
            if not ok:
                self.log_panel.log(f"HATA: Snapshot yazılamadı: {snap_path}")
                snap_path_str = ""
            else:
                snap_path_str = str(snap_path)

            msg = f"{ts} | {ev} | SNAP: {snap_path_str}"
            self.log_panel.log(msg)
            self.last_event_panel.set_text(msg)

            self.db.insert_event(ts, bottle_id, ev, snap_path_str)

        self.video.set_frame(annotated)
        self._update_metrics(tick_start)