from PyQt6.QtWidgets import QApplication
from signal import signal, SIGINT, SIG_DFL

from .main_window import MainWindow


def main():
    signal(SIGINT, SIG_DFL)

    app = QApplication([])
    _window = MainWindow()
    app.exec()


if __name__ == '__main__':
    main()
