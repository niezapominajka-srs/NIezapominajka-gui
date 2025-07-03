#!/usr/bin/env python
# This file is part of Niezapominajka flashcard app
# License: GNU GPL version 3 or later
# Copyright (C) 2025 Wiktor Malinkiewicz

from PyQt6.QtWidgets import (
    QDockWidget,
    QLabel,
    QMainWindow,
    QStackedWidget,
    QToolBar
)
from PyQt6.QtGui import QAction, QIcon
from importlib import resources
from PyQt6.QtCore import QTimer, pyqtSignal, Qt

from .home_screen import HomeScreen
from .deck_review import DeckReview


class Toolbar(QToolBar):
    def __init__(self):
        super().__init__()
        fallback_icon = QIcon(str(
            resources.files('niezapominajka_gui').joinpath('res', 'home.svg')
        ))
        icon = QIcon.fromTheme('go-home', fallback_icon)

        self.go_home_actn = QAction(icon, 'home')
        self.go_home_actn.setToolTip('Go to homescreen')
        self.addAction(self.go_home_actn)


class StatusBar(QDockWidget):
    def __init__(self):
        super().__init__()
        self.status = QLabel()
        self.setWidget(self.status)
        self.status.setWordWrap(True)

    def set_status(self, text):
        self.status.setText(text)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Niezapominajka')
        self.status_bar = StatusBar()
        self.status_bar.hide()
        self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, self.status_bar)

        self.toolbar = Toolbar()
        central_widget = StackedWidget()

        self.addToolBar(self.toolbar)
        self.setCentralWidget(central_widget)
        self.show()

        self.toolbar.go_home_actn.triggered.connect(central_widget.go_home)
        central_widget.alert_sig.connect(self.show_status_bar)

    def show_status_bar(self, text):
        self.status_bar.set_status(text)
        self.status_bar.show()


class StackedWidget(QStackedWidget):
    alert_sig = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.home_screen = HomeScreen()
        self.deck_review = DeckReview()

        self.addWidget(self.home_screen)
        self.addWidget(self.deck_review)

        self.home_screen.review_sig.connect(self.start_review)
        self.deck_review.alert_sig.connect(self.abort_review)

    def abort_review(self, text):
        self.alert_sig.emit(text)
        QTimer.singleShot(0, self.go_home)

    def go_home(self):
        self.home_screen.refresh()
        self.setCurrentWidget(self.home_screen)

    def start_review(self, deck_name):
        self.deck_review.start_session(deck_name)
        self.setCurrentWidget(self.deck_review)
