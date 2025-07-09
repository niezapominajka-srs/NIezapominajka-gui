#!/usr/bin/env python
# This file is part of Niezapominajka flashcard app
# License: GNU GPL version 3 or later
# Copyright (C) 2025 Wiktor Malinkiewicz

from PySide6.QtWidgets import QApplication
from signal import signal, SIGINT, SIG_DFL

from .main_window import MainWindow


def main():
    signal(SIGINT, SIG_DFL)

    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
