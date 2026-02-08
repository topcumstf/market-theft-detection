from PyQt5.QtWidgets import QTextEdit


class LogWidget(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setMinimumWidth(320)  # log alanı ezilmesin

    def log(self, message: str) -> None:
        self.append(message)