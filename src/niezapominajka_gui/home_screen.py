#!/usr/bin/env python
# This file is part of Niezapominajka flashcard app
# License: GNU GPL version 3 or later
# Copyright (C) 2025 Wiktor Malinkiewicz

from PyQt6.QtCore import Qt, QModelIndex, QAbstractListModel, QRect, pyqtSignal
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QStyledItemDelegate,
    QWidget,
    QStyle,
    QListView
)
from PyQt6.QtGui import QPen, QPalette, QColor

from niezapominajka import review


class DeckListModel(QAbstractListModel):
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
        if not index.isValid() or not (0 <= index.row() < len(self._data)):
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()]

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
            data = model.data(model.index(i, 0), Qt.ItemDataRole.DisplayRole)
            width = font_metrics.horizontalAdvance(data[0])
            if width > max_width: max_width = width

        self.max_width = int(max_width * 1.1)

    def paint(self, painter, option, index):
        name, count = index.data(Qt.ItemDataRole.DisplayRole)
        painter.save()

        name_rect_width = min(self.max_width, int(option.rect.width() * .7))

        name_rect = QRect(
            (option.rect.width() - name_rect_width) // 2,
            option.rect.y(),
            name_rect_width,
            option.rect.height()
        )

        padding = option.rect.width() // 50
        count_rect = QRect(
            name_rect.right() + padding,
            option.rect.y(),
            option.rect.width() - name_rect.right() - padding,
            option.rect.height()
        )

        pen = QPen(option.palette.color(QPalette.ColorRole.Accent))
        pen.setWidthF(0.5)
        painter.setPen(pen)
        painter.drawLine(name_rect.topLeft(), name_rect.bottomLeft())
        painter.drawLine(name_rect.topRight(), name_rect.bottomRight())
        painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())

        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
            painter.setPen(QPen(option.palette.color(QPalette.ColorRole.HighlightedText)))
        else:
            painter.setPen(QPen(option.palette.color(QPalette.ColorRole.WindowText)))
        highlight = QColor(option.palette.highlight())
        highlight.setAlpha(100)
        if option.state & QStyle.StateFlag.State_MouseOver:
            painter.fillRect(option.rect, highlight)

        painter.drawText(name_rect, Qt.AlignmentFlag.AlignCenter, name)
        if count != 0:
            painter.drawText(count_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, str(count))

        painter.restore()

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(size.height() + option.fontMetrics.height() // 2)
        return size


class HomeScreen(QWidget):
    review_sig = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        self.deck_list_widget = QListView()
        self.deck_list_widget.setAlternatingRowColors(True)
        self.model = DeckListModel()

        self.deck_list_widget.setModel(self.model)

        self.delegate = DeckListDelegate(self.deck_list_widget)
        self.deck_list_widget.setItemDelegate(self.delegate)

        self.refresh()

        layout.addWidget(self.deck_list_widget)

        self.deck_list_widget.activated.connect(
            lambda index: self.review_sig.emit(self.model.data(index)[0])
        )

    def refresh(self):
        data = [(x['name'], x['num']) for x in review.get_deck_list()]
        self.model.set_data(data)
        self.delegate.recalculate_max_width()
        self.deck_list_widget.setCurrentIndex(self.model.index(0,0))
