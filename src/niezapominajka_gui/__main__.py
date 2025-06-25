#!/usr/bin/env python
# This file is part of Niezapominajka flashcard app
# License: GNU GPL version 3 or later
# Copyright (C) 2025 Wiktor Malinkiewicz

from signal import SIGINT, signal, SIG_DFL
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QToolBar
)
from PyQt6.QtGui import QIcon
from importlib import resources

from .home_screen import HomeScreen
from .deck_review import _review_session


class Toolbar(QToolBar):
    def __init__(self):
        super().__init__()

        home = QPushButton()
        icon = resources.files('niezapominajka_gui').joinpath('res', 'home.svg')
        home.setIcon(QIcon(str(icon)))
        home.clicked.connect(lambda: self.go_home(self.parent()))
        self.addWidget(home)

    def go_home(self, parent):
        global _review_session
        if _review_session:
            _review_session.close_db()
            _review_session = None

        parent.setCentralWidget(HomeScreen())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Niezapominajka')
        self.setCentralWidget(HomeScreen())
        self.addToolBar(Toolbar())
        self.show()


def main():
    app = QApplication([])
    _window = MainWindow()
    app.exec()


signal(SIGINT, SIG_DFL)


if __name__ == '__main__':
    main()
