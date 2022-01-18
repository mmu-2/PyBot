from random import random
import sys
from enum import IntEnum
from PyQt6.QtWidgets import (QWidget, QSlider, QApplication,
QHBoxLayout, QVBoxLayout, QLabel, QFrame, QPushButton,
QRadioButton, QToolButton)
from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QFont, QColor, QPen, QIcon


class Communicate(QObject):
    cancel = pyqtSignal(QObject)

class Card(IntEnum):
    # NOOP = 0
    MOVE = 1
    LEFT_CLICK_PRESS = 2
    LEFT_CLICK_RELEASE = 3
    RIGHT_CLICK_PRESS = 4
    RIGHT_CLICK_RELEASE = 5
    MIDDLE_CLICK_PRESS = 6
    MIDDLE_CLICK_RELEASE = 7
    SCROLL = 8
    KEY_PRESS = 9
    KEY_RELEASE = 10
    SPECIAL_KEY_PRESS = 11
    SPECIAL_KEY_RELEASE = 12


class QCard(QWidget):

    def __init__(self, parent = None, action = Card.MOVE, delay_s = 0, data = None):
        super().__init__()

        self.initUI(parent, action, delay_s, data)

    def initUI(self, menu, action, delay_s, data):
        
        self.setParent(menu)
        self.action = action
        self.delay = delay_s
        self.data = data

        self.c = Communicate()
        self.c.cancel[QObject].connect(menu.cancelCard)
        layout = QHBoxLayout()
        a = QLabel('Card: {} after {:.5f} s'.format(self.action.name, self.delay))
        cancel = QToolButton(self)

        cancel.setText('X')
        cancel.clicked.connect(self.close_card)
        layout.addWidget(a)
        layout.addWidget(cancel)
        self.setLayout(layout)

    def close_card(self):
        self.c.cancel.emit(self)
