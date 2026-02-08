from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel


class LastEventPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.title = QLabel("Son Olay:")
        self.title.setStyleSheet("font-weight: 700;")


        self.setMinimumHeight(120)


        self.value = QLabel("—")
        self.value.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.value.setWordWrap(True)
        self.value.setStyleSheet("padding: 6px; border: 1px solid #666; border-radius: 6px;")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(self.title)
        layout.addWidget(self.value)
        self.setLayout(layout)

    def set_text(self, text: str):
        self.value.setText(text)