import sys, random, time
from enum import IntEnum
from PyQt6.QtWidgets import (QWidget, QSlider, QApplication,
QHBoxLayout, QVBoxLayout, QLabel, QFrame, QPushButton,
QRadioButton, QToolButton, QLineEdit, QComboBox, QMenu)
from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QFont, QColor, QPen, QIcon

from pynput.mouse import Button as Mouse_Button
from pynput import keyboard

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

        self.initUI(parent, action, delay_s, data) #if inherited, will call child's initUI

    def initUI(self, menu, action, delay_s, data):
        
        self.setParent(menu)
        self.action = action
        self.delay = delay_s
        self.data = data

        self.c = Communicate()
        self.c.cancel[QObject].connect(menu.cancelCard)
        self.frame = QFrame()
        self.frame.setStyleSheet("""
        .QFrame::hover
        {
            background-color : lightgrey;
        }
        """)
        layout = QHBoxLayout(self.frame)
        card_dropdown = QComboBox(self)
        for i in Card:
            card_dropdown.addItem(str(i))
        card_dropdown.setCurrentIndex(self.action-1)
        card_dropdown.currentIndexChanged.connect(self.index_changed)

        delay_label = QLabel(' after ')
        delay_edit = QLineEdit(f'{self.delay:.5f}', self)
        delay_edit.textChanged[str].connect(self.change_delay)
        unit_label = QLabel('seconds')
        

        cancel = QToolButton(self)
        cancel.setText('X')
        cancel.clicked.connect(self.close_card)

        layout.addWidget(card_dropdown)
        layout.addWidget(delay_label)
        layout.addWidget(delay_edit)
        layout.addWidget(unit_label)

        layout.addWidget(cancel)
        self.frame.setLayout(layout)

        self.frame.mouseReleaseEvent=self.expand_info
        # self.mouseReleaseEvent=self.expand_info

    def expand_info(self, e):

        self.infoWindow = QFrame()
        # menu.move(e.globalPosition().toPoint())

        layout = QHBoxLayout(self.infoWindow)
        layout.addWidget(QLabel("Default Window",self.infoWindow))

        self.infoWindow.move(e.globalPosition().toPoint())
        self.infoWindow.show()

    
    def index_changed(self, index):

        #QComboBox index starts at 0, but my enum starts at 1
        self.action = Card(index+1)

    def change_delay(self, value):
        try:
            new_delay = float(value)
            if new_delay < 0:
                raise ValueError()
            self.delay = new_delay
        except ValueError:
            print('Delay is not set.')
            return

    def play_card(self, *args):
        print('Not implemented yet')

    def close_card(self):
        self.c.cancel.emit(self)


class QBasicCard(QCard):

    def __init__(self, parent = None, action = Card.MOVE, delay_s = 0, data = None):
        super().__init__(parent, action, delay_s, data)
        # self.initUI(parent, action, delay_s, data)

    def play_card(self, mouse = None, keyboard_controller = None):

        if self.action <= Card.SCROLL: #mouse event
            mouse.position = self.data['position']
            if self.action == Card.MOVE:
                pass
            elif self.action == Card.LEFT_CLICK_PRESS:
                mouse.press(Mouse_Button.left)
            elif self.action == Card.LEFT_CLICK_RELEASE:
                mouse.release(Mouse_Button.left)
            elif self.action == Card.RIGHT_CLICK_PRESS:
                mouse.press(Mouse_Button.right)
            elif self.action == Card.RIGHT_CLICK_RELEASE:
                mouse.release(Mouse_Button.right)
            elif self.action == Card.MIDDLE_CLICK_PRESS:
                mouse.press(Mouse_Button.middle)
            elif self.action == Card.MIDDLE_CLICK_RELEASE:
                mouse.release(Mouse_Button.middle)
            elif self.action == Card.SCROLL:
                (dx, dy) = self.data['movement']
                mouse.scroll(dx, dy)
        elif self.action <= Card.SPECIAL_KEY_RELEASE: #keyboard event
            if self.action == Card.KEY_PRESS:
                keyboard_controller.press(keyboard.KeyCode.from_vk(self.data['vk']))
            elif self.action == Card.KEY_RELEASE:
                keyboard_controller.release(keyboard.KeyCode.from_vk(self.data['vk']))
            elif self.action == Card.SPECIAL_KEY_PRESS:
                if self.data['is_media'] == True:
                    media_key = keyboard.KeyCode._from_media(self.data['vk'])
                    key = keyboard.Key(media_key)
                    print(f'press: {key}')
                    keyboard_controller.press(key)
                else:
                    keyboard_controller.press(keyboard.KeyCode.from_vk(self.data['vk']))
            elif self.action == Card.SPECIAL_KEY_RELEASE:
                if self.data['is_media'] == True:
                    media_key = keyboard.KeyCode._from_media(self.data['vk'])
                    key = keyboard.Key(media_key)
                    print(f'release : {key}')
                    keyboard_controller.release(key)
                else:
                    keyboard_controller.release(keyboard.KeyCode.from_vk(self.data['vk']))
        else:
            print("Not supported BasicCard action.")

    def close_card(self):
        self.c.cancel.emit(self)

    def expand_info(self, e):

        self.infoWindow = QFrame()
        # menu.move(e.globalPosition().toPoint())
        self.infoWindowLayout = QVBoxLayout()
        self.infoWindowHLayouts = []

        if self.action <= Card.MIDDLE_CLICK_RELEASE: #all mouse movement
            self.infoWindowHLayouts.append(QHBoxLayout())
            self.infoWindowHLayouts[-1].addWidget(QLabel('Position: (',self.infoWindow))
            print(self.data['position'])
            x = int(self.data['position'][0])
            y = int(self.data['position'][1])
            xLineEdit = QLineEdit(str(x),self.infoWindow)
            yLineEdit = QLineEdit(str(y),self.infoWindow)
            xLineEdit.textChanged[str].connect(self.change_x)
            yLineEdit.textChanged[str].connect(self.change_y)
            self.infoWindowHLayouts[-1].addWidget(xLineEdit)
            self.infoWindowHLayouts[-1].addWidget(QLabel(', ',self.infoWindow))
            self.infoWindowHLayouts[-1].addWidget(yLineEdit)
            self.infoWindowHLayouts[-1].addWidget(QLabel(')',self.infoWindow))
        elif self.action == Card.SCROLL:
            self.infoWindowHLayouts.append(QHBoxLayout())
            self.infoWindowHLayouts[-1].addWidget(QLabel('Position: (',self.infoWindow))
            print(self.data['position'])
            x = int(self.data['position'][0])
            y = int(self.data['position'][1])
            xLineEdit = QLineEdit(str(x),self.infoWindow)
            yLineEdit = QLineEdit(str(y),self.infoWindow)
            xLineEdit.textChanged[str].connect(self.change_x)
            yLineEdit.textChanged[str].connect(self.change_y)
            self.infoWindowHLayouts[-1].addWidget(xLineEdit)
            self.infoWindowHLayouts[-1].addWidget(QLabel(', ',self.infoWindow))
            self.infoWindowHLayouts[-1].addWidget(yLineEdit)
            self.infoWindowHLayouts[-1].addWidget(QLabel(')',self.infoWindow))
            ##################################################################
            self.infoWindowHLayouts.append(QHBoxLayout())
            self.infoWindowHLayouts[-1].addWidget(QLabel('Movement: (',self.infoWindow))
            print(self.data['movement'])
            dx = int(self.data['movement'][0])
            dy = int(self.data['movement'][1])
            dxLineEdit = QLineEdit(str(dx),self.infoWindow)
            dyLineEdit = QLineEdit(str(dy),self.infoWindow)
            dxLineEdit.textChanged[str].connect(self.change_dx)
            dyLineEdit.textChanged[str].connect(self.change_dy)
            self.infoWindowHLayouts[-1].addWidget(dxLineEdit)
            self.infoWindowHLayouts[-1].addWidget(QLabel(', ',self.infoWindow))
            self.infoWindowHLayouts[-1].addWidget(dyLineEdit)
            self.infoWindowHLayouts[-1].addWidget(QLabel(')',self.infoWindow))

        for HLayout in self.infoWindowHLayouts:
            self.infoWindowLayout.addLayout(HLayout)

        print(self.infoWindowHLayouts)
        print(self.infoWindowLayout)
        self.infoWindow.setLayout(self.infoWindowLayout)
        self.infoWindow.move(e.globalPosition().toPoint())
        self.infoWindow.show()
    
    def change_x(self, value):
        try:
            new_x = float(value)
            if new_x < 0:
                raise ValueError()
            self.data['position'][0] = new_x
        except ValueError:
            print('x is not set.')
            return

    def change_y(self, value):
        try:
            new_y = float(value)
            if new_y < 0:
                raise ValueError()
            self.data['position'][1] = new_y
        except ValueError:
            print('y is not set.')
            return

    def change_dx(self, value):
        try:
            new_dx = float(value)
            if new_dx < 0:
                raise ValueError()
            self.data['movement'][0] = new_dx
        except ValueError:
            print('dx is not set.')
            return

    def change_dy(self, value):
        try:
            new_dy = float(value)
            if new_dy < 0:
                raise ValueError()
            self.data['movement'][1] = new_dy
        except ValueError:
            print('dy is not set.')
            return