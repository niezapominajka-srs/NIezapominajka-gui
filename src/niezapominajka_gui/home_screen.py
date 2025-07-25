#!/usr/bin/env python
# This file is part of Niezapominajka flashcard app
# License: GNU GPL version 3 or later
# Copyright (C) 2025 Wiktor Malinkiewicz

from PySide6.QtCore import Qt, QModelIndex, QAbstractListModel, QRect, Signal as qtSignal
from PySide6.QtWidgets import (
    QVBoxLayout,
    QStyledItemDelegate,
    QWidget,
    QStyle,
    QListView,
    QLabel
)
from PySide6.QtGui import QPen, QPalette
from niezapominajka import review


class DeckListModel(QAbstractListModel):
    DeckNameRole = Qt.ItemDataRole.UserRole + 1
    CardCountRole = Qt.ItemDataRole.UserRole + 2

    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self._data = data or []

    def set_data(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        row = self._data[index.row()]

        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.AccessibleTextRole:
            return f'{row[0]}, {row[1]} cards'

        if role == self.DeckNameRole:
            return row[0]

        if role == self.CardCountRole:
            return row[1]

        return None


class DeckListDelegate(QStyledItemDelegate):
    def __init__(self, deck_list_widget):
        super().__init__(deck_list_widget)
        self.deck_list_widget = deck_list_widget
        self.recalculate_max_width()

    def recalculate_max_width(self):
        font_metrics = self.deck_list_widget.fontMetrics()
        model = self.deck_list_widget.model()
        max_width = 0
        for i in range(model.rowCount()):
            deck_name = model.data(model.index(i), DeckListModel.DeckNameRole)
            width = font_metrics.horizontalAdvance(deck_name)
            if width > max_width: max_width = width

        self.name_required_width = int(max_width * 1.1)

    def paint(self, painter, option, index):
        name = index.data(DeckListModel.DeckNameRole)
        count = index.data(DeckListModel.CardCountRole)
        painter.save()

        NAME_RECT_MAX_WIDTH = option.rect.width() * .7
        name_rect_width = min(self.name_required_width, NAME_RECT_MAX_WIDTH)

        name_rect = QRect(
            (option.rect.width() - name_rect_width) // 2,
            option.rect.y(),
            name_rect_width,
            option.rect.height()
        )

        PADDING = option.rect.width() // 50
        count_rect = QRect(
            name_rect.right() + PADDING,
            option.rect.y(),
            option.rect.width() - name_rect.right() - PADDING,
            option.rect.height()
        )

        highlight_selection = option.palette.highlight().color()
        highlight_selection.setAlpha(180)
        highlight_hover = option.palette.highlight().color()
        highlight_hover.setAlpha(90)

        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(option.rect, highlight_selection)
            painter.setPen(QPen(option.palette.color(QPalette.ColorRole.HighlightedText)))
        else:
            painter.setPen(QPen(option.palette.color(QPalette.ColorRole.WindowText)))
        if option.state & QStyle.StateFlag.State_MouseOver and count != 0:
            painter.fillRect(option.rect, highlight_hover)

        if count == 0:
            text_color = painter.pen().color()
            text_color.setAlpha(140)
            painter.setPen(QPen(text_color))
        painter.drawText(count_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, str(count))
        painter.drawText(name_rect, Qt.AlignmentFlag.AlignCenter, name)

        pen = QPen(option.palette.color(QPalette.ColorRole.Accent))
        pen.setWidthF(0.5)
        painter.setPen(pen)
        painter.drawLine(name_rect.topLeft(), name_rect.bottomLeft())
        painter.drawLine(name_rect.topRight(), name_rect.bottomRight())
        painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())

        painter.restore()

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(size.height() + option.fontMetrics.height() // 2)
        return size


class HomeScreen(QWidget):
    review_sig = qtSignal(str)

    def __init__(self):
        super().__init__()
        self.cached_data = None
        self.empty_decklist_label = QLabel('No decks :(')
        self.empty_decklist_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.empty_decklist_label.hide()

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        self.deck_list_widget = QListView()
        self.deck_list_widget.setAlternatingRowColors(True)
        self.model = DeckListModel()

        self.deck_list_widget.setModel(self.model)

        self.delegate = DeckListDelegate(self.deck_list_widget)
        self.deck_list_widget.setItemDelegate(self.delegate)

        self.refresh()

        layout.addWidget(self.empty_decklist_label, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.deck_list_widget)

        self.deck_list_widget.activated.connect(
            lambda index: self.review_sig.emit(self.model.data(index, DeckListModel.DeckNameRole))
        )

    def refresh(self):
        data = [(x['name'], x['num']) for x in review.get_deck_list()]
        if data: self.empty_decklist_label.hide()
        else:
            self.empty_decklist_label.show()
            self.empty_decklist_label.setFocus()

        if self.cached_data != data:
            self.model.set_data(data)
            self.delegate.recalculate_max_width()
            self.deck_list_widget.setCurrentIndex(self.model.index(0))
            self.cached_data = data
