from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel


class StatusPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.lbl_title = QLabel("Durum:")
        self.lbl_title.setStyleSheet("font-weight: 700;")

        self.lbl_status = QLabel("STOPPED")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setMinimumWidth(120)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_status)
        layout.addStretch(1)
        self.setLayout(layout)

        self.set_running(False)

    def set_running(self, running: bool):
        if running:
            self.lbl_status.setText("RUNNING")
            self.lbl_status.setStyleSheet(
                "background: #1f7a1f; color: white; padding: 6px; border-radius: 6px; font-weight: 700;"
            )
        else:
            self.lbl_status.setText("STOPPED")
            self.lbl_status.setStyleSheet(
                "background: #7a1f1f; color: white; padding: 6px; border-radius: 6px; font-weight: 700;"
            )