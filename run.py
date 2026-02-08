import sys
from PyQt5.QtWidgets import QApplication
from app.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()  # tam ekran
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())