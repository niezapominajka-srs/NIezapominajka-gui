#!/usr/bin/env python
# This file is part of Niezapominajka flashcard app
# License: GNU GPL version 3 or later
# Copyright (C) 2025 Wiktor Malinkiewicz

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget
)
from PyQt6.QtGui import (
    QKeySequence,
    QShortcut
)

from niezapominajka import review


_review_session = None


class DeckReview(QWidget):
    def __init__(self, deck_name):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.card_widget = QLabel()
        self.card_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card_widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        layout.addWidget(self.card_widget)

        self.good = QPushButton('(g)ood')
        self.bad = QPushButton('(b)ad')
        buttons = (self.good, self.bad)
        for x in buttons:
            size_policy = x.sizePolicy()
            size_policy.setRetainSizeWhenHidden(True)
            x.setSizePolicy(size_policy)
            layout.addWidget(x)

        shortcut = QShortcut(QKeySequence('g'), self)
        shortcut.activated.connect(lambda: self.answered(1))
        self.good.clicked.connect(lambda: self.answered(1))

        shortcut = QShortcut(QKeySequence('b'), self)
        shortcut.activated.connect(lambda: self.answered(0))
        self.bad.clicked.connect(lambda: self.answered(0))

        self.answer_text = None
        self.question_text = None
        global _review_session
        _review_session = review.ReviewSession(deck_name)

        self.deal_a_card()

    def deal_a_card(self):
        self.good.hide()
        self.bad.hide()
        while True:
            try:
                cards_content = _review_session.get_next_card()
                if cards_content:
                    self.question_text = cards_content[0]
                    self.answer_text = cards_content[1]
                    self.card_widget.setText(self.question_text)
                    self.is_question = True
                    break
                else:
                    self.card_widget.setText('Empty deck :)')
                    self.card_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                    self.answer_text = None
                    self.question_text = None
                    break
            except FileNotFoundError:
                # todo: popup?
                continue

    def turn_the_card(self):
        if self.answer_text is not None:
            if self.is_question:
                self.card_widget.setText(self.answer_text)
                self.is_question = False
            else:
                self.card_widget.setText(self.question_text)
                self.is_question = True
            self.good.show()
            self.bad.show()

    def mouseReleaseEvent(self, _event):
        self.turn_the_card()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return:
            self.turn_the_card()

    def answered(self, score):
        _review_session.submit_score(score)
        self.deal_a_card()
