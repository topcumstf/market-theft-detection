from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

from app.ui.widgets.log_widget import LogWidget


class LogPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.title = QLabel("LOG / BİLGİLENDİRME EKRANI")
        self.title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.title.setStyleSheet("font-weight: 700; padding: 6px;")

        self.log_widget = LogWidget()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(self.title)
        layout.addWidget(self.log_widget)

        self.setLayout(layout)

    def log(self, message: str) -> None:
        self.log_widget.log(message)