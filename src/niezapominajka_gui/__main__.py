from PyQt6.QtWidgets import QApplication
from signal import signal, SIGINT, SIG_DFL

from .main_window import MainWindow


def main():
    app = QApplication([])
    _window = MainWindow()
    app.exec()


signal(SIGINT, SIG_DFL)

if __name__ == '__main__':
    main()
