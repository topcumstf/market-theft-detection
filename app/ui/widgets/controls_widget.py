from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QComboBox, QSlider
)


class ControlsWidget(QWidget):
    start_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    refresh_cameras_clicked = pyqtSignal()
    camera_changed = pyqtSignal(int)

    conf_changed = pyqtSignal(float)
    near_time_changed = pyqtSignal(float)
    disappear_time_changed = pyqtSignal(float)

    export_csv_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # --- üst satır: start/stop + kamera + export
        self.btn_start = QPushButton("Start")
        self.btn_stop = QPushButton("Stop")
        self.btn_stop.setEnabled(False)

        self.lbl_cam = QLabel("Kamera:")
        self.cmb_camera = QComboBox()
        self.btn_refresh = QPushButton("Yenile")

        self.btn_export = QPushButton("CSV Export")

        top_row = QHBoxLayout()
        top_row.addWidget(self.btn_start)
        top_row.addWidget(self.btn_stop)
        top_row.addSpacing(20)
        top_row.addWidget(self.lbl_cam)
        top_row.addWidget(self.cmb_camera)
        top_row.addWidget(self.btn_refresh)
        top_row.addSpacing(20)
        top_row.addWidget(self.btn_export)
        top_row.addStretch(1)

        # --- alt satır: slider’lar
        self.lbl_conf = QLabel("Confidence: 0.45")
        self.sld_conf = QSlider(Qt.Horizontal)
        self.sld_conf.setMinimum(10)
        self.sld_conf.setMaximum(90)
        self.sld_conf.setValue(45)

        self.lbl_near = QLabel("Yakınlık süresi: 3.0s")
        self.sld_near = QSlider(Qt.Horizontal)
        self.sld_near.setMinimum(1)
        self.sld_near.setMaximum(10)
        self.sld_near.setValue(3)

        self.lbl_dis = QLabel("Kaybolma süresi: 3.0s")
        self.sld_dis = QSlider(Qt.Horizontal)
        self.sld_dis.setMinimum(1)
        self.sld_dis.setMaximum(10)
        self.sld_dis.setValue(3)

        bottom_row = QHBoxLayout()
        bottom_row.addWidget(self.lbl_conf)
        bottom_row.addWidget(self.sld_conf, 1)
        bottom_row.addSpacing(16)
        bottom_row.addWidget(self.lbl_near)
        bottom_row.addWidget(self.sld_near, 1)
        bottom_row.addSpacing(16)
        bottom_row.addWidget(self.lbl_dis)
        bottom_row.addWidget(self.sld_dis, 1)

        layout = QVBoxLayout()
        layout.addLayout(top_row)
        layout.addLayout(bottom_row)
        self.setLayout(layout)

        # --- bağlantılar
        self.btn_start.clicked.connect(self._on_start)
        self.btn_stop.clicked.connect(self._on_stop)
        self.btn_refresh.clicked.connect(self.refresh_cameras_clicked.emit)
        self.cmb_camera.currentIndexChanged.connect(self._on_camera_changed)

        self.sld_conf.valueChanged.connect(self._on_conf_changed)
        self.sld_near.valueChanged.connect(self._on_near_changed)
        self.sld_dis.valueChanged.connect(self._on_dis_changed)

        self.btn_export.clicked.connect(self.export_csv_clicked.emit)

    def set_cameras(self, camera_indices):
        self.cmb_camera.blockSignals(True)
        self.cmb_camera.clear()
        for idx in camera_indices:
            self.cmb_camera.addItem(f"Camera {idx}", idx)
        self.cmb_camera.blockSignals(False)

    def selected_camera_index(self) -> int:
        data = self.cmb_camera.currentData()
        return int(data) if data is not None else 0

    def set_running(self, running: bool):
        self.btn_start.setEnabled(not running)
        self.btn_stop.setEnabled(running)
        self.cmb_camera.setEnabled(not running)
        self.btn_refresh.setEnabled(not running)

        self.btn_export.setEnabled(True)

        self.sld_conf.setEnabled(True)
        self.sld_near.setEnabled(True)
        self.sld_dis.setEnabled(True)

    def _on_start(self):
        self.set_running(True)
        self.start_clicked.emit()

    def _on_stop(self):
        self.set_running(False)
        self.stop_clicked.emit()

    def _on_camera_changed(self, _):
        self.camera_changed.emit(self.selected_camera_index())

    def _on_conf_changed(self, v: int):
        conf = v / 100.0
        self.lbl_conf.setText(f"Confidence: {conf:.2f}")
        self.conf_changed.emit(conf)

    def _on_near_changed(self, v: int):
        t = float(v)
        self.lbl_near.setText(f"Yakınlık süresi: {t:.1f}s")
        self.near_time_changed.emit(t)

    def _on_dis_changed(self, v: int):
        t = float(v)
        self.lbl_dis.setText(f"Kaybolma süresi: {t:.1f}s")
        self.disappear_time_changed.emit(t)