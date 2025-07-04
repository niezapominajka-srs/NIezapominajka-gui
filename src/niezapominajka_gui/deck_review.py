#!/usr/bin/env python
# This file is part of Niezapominajka flashcard app
# License: GNU GPL version 3 or later
# Copyright (C) 2025 Wiktor Malinkiewicz

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget
)
from PyQt6.QtGui import QKeySequence

from niezapominajka import review


class Card(QLabel):
    clicked_sig = pyqtSignal()

    def mouseReleaseEvent(self, event):
        self.clicked_sig.emit()


class Line(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.HLine)


class DeckReview(QWidget):
    alert_sig = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.session = None
        self.is_question = None

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.q_or_ans_label = QLabel()
        layout.addWidget(self.q_or_ans_label, 0, Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(Line())

        self.card_widget = Card()
        # alignment must be set here not in the addWidget() cause
        # some weird shit happens then and only the part of the card_widget
        # with text is clickable
        self.card_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card_widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.card_widget.clicked_sig.connect(self.turn_the_card)
        layout.addWidget(self.card_widget, 1)

        layout.addWidget(Line())

        self.easy = QPushButton('(e)asy')
        self.hard = QPushButton('(h)ard')
        for x in (self.easy, self.hard):
            size_policy = x.sizePolicy()
            size_policy.setRetainSizeWhenHidden(True)
            x.setSizePolicy(size_policy)
            layout.addWidget(x)

        self.easy.clicked.connect(lambda: self.answered(1))
        self.easy.setShortcut(QKeySequence('e'))

        self.hard.clicked.connect(lambda: self.answered(0))
        self.hard.setShortcut(QKeySequence('h'))

        self.answer_text = None
        self.question_text = None

    def start_session(self, deck_name):
        self.session = review.ReviewSession(deck_name)
        self.deal_a_card()

    def deal_a_card(self):
        self.easy.hide()
        self.hard.hide()
        try:
            cards_content = self.session.get_next_card()
            if cards_content:
                self.question_text = cards_content[0]
                self.answer_text = cards_content[1]
                self.card_widget.setText(self.question_text)
                self.is_question = True
                self.q_or_ans_label.setText('question')
            else:
                self.card_widget.setText('Empty deck :)')
                self.card_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                self.answer_text = None
                self.question_text = None
                self.q_or_ans_label.setText('')
        except FileNotFoundError:
            self.alert_sig.emit("Aborted. A card wasn't found, even though it existed when cards for review were being assembled")

    def turn_the_card(self):
        if self.answer_text is not None:
            if self.is_question:
                self.card_widget.setText(self.answer_text)
                self.is_question = False
                self.q_or_ans_label.setText('answer')
            else:
                self.card_widget.setText(self.question_text)
                self.is_question = True
                self.q_or_ans_label.setText('question')
            self.easy.show()
            self.hard.show()

    def answered(self, score):
        self.session.submit_score(score)
        self.deal_a_card()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            self.turn_the_card()

    def hideEvent(self, event):
        if not event.spontaneous():
            if self.session: self.session.close_db()
