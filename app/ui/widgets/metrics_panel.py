from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel


class MetricsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.lbl_fps = QLabel("FPS: —")
        self.lbl_lat = QLabel("Latency: — ms")

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addWidget(self.lbl_fps)
        layout.addWidget(self.lbl_lat)
        layout.addStretch(1)
        self.setLayout(layout)

    def set_metrics(self, fps: float, latency_ms: float):
        self.lbl_fps.setText(f"FPS: {fps:.1f}")
        self.lbl_lat.setText(f"Latency: {latency_ms:.0f} ms")