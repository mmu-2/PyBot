import sys, time, random, json
from PyQt6.QtWidgets import (QApplication, QWidget, QToolTip, 
QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, 
QCheckBox, QScrollArea, QListWidget)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from custom_widgets import QCard, Card

from pynput import mouse
from pynput.mouse import Button as Mouse_Button
from pynput.mouse import Controller as Mouse_Controller
from pynput import keyboard
from pynput.keyboard import Key as Keyboard_Key
from pynput.keyboard import Controller as Keyboard_Controller


class Menu(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()
        self.mouse_events = []
        self.keyboard_events = []
        self.events = []
        self.recording = False
        self.track_moving = False
        self.current_time = time.time()
        self.cards = []
        self.speed = 1
        self.repeat = 1
        self.randomizer = 1
        self.randomize = False
        self.filename = ''
        self.playing = False

    def initUI(self):
        # QToolTip.setFont(QFont('SansSerif', 10))
        # self.setToolTip('This is a <b>QWidget</b> widget')

        vbox = QVBoxLayout(self)

        load = QPushButton('Load', self)
        load.clicked.connect(self.loadFile)
        export = QPushButton('Export', self)
        export.clicked.connect(self.exportFile)
        file_text = QLineEdit(self)
        file_text.textChanged[str].connect(self.change_filename)

        file_box = QHBoxLayout()
        file_box.addWidget(load)
        file_box.addWidget(export)
        file_box.addWidget(file_text)

        vbox.addLayout(file_box)

#########################################################################

        randomize = QCheckBox('Randomize?', self)
        randomize.stateChanged.connect(self.toggle_randomizer)
        rand_label = QLabel(self)
        rand_label.setText('Multiplier (def=1):')
        rand_amt = QLineEdit(self)
        rand_amt.textChanged[str].connect(self.change_randomizer)

        randomizer_box = QHBoxLayout()
        randomizer_box.addWidget(randomize)
        randomizer_box.addSpacing(25)
        randomizer_box.addWidget(rand_label)
        randomizer_box.addWidget(rand_amt)

        vbox.addLayout(randomizer_box)

#########################################################################

        track_move_option = QCheckBox('Track Moves?', self)
        track_move_option.stateChanged.connect(self.toggle_track_move)
        repeat_label = QLabel(self)
        repeat_label.setText('Repeat (def=1):')
        repeat_amt = QLineEdit(self)
        repeat_amt.textChanged[str].connect(self.change_repeat)

        extra_options_box = QHBoxLayout()
        extra_options_box.addWidget(track_move_option)
        extra_options_box.addWidget(repeat_label)
        extra_options_box.addWidget(repeat_amt)

        vbox.addLayout(extra_options_box)

#########################################################################

        speed_label = QLabel(self)
        speed_label.setText('Speed Multiplier (def=1):')
        speed_amt = QLineEdit(self)
        speed_amt.textChanged[str].connect(self.change_speed)

        speed_box = QHBoxLayout()
        speed_box.addWidget(speed_label)
        speed_box.addWidget(speed_amt)

        vbox.addLayout(speed_box)

#########################################################################

        self.record_button = QPushButton('Record', self)
        self.record_button.clicked.connect(self.record)
        self.play_button = QPushButton('Play', self)
        self.play_button.clicked.connect(self.play)
        self.exit = QPushButton('Exit', self)
        self.exit.clicked.connect(QApplication.instance().quit)

        interact_box = QHBoxLayout()
        interact_box.addWidget(self.record_button)
        interact_box.addWidget(self.play_button)
        interact_box.addWidget(self.exit)

        vbox.addLayout(interact_box)

#########################################################################

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget(scroll_area) #filler widget
        self.cardLayout = QVBoxLayout(scroll_content)
        self.cardLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_content.setLayout(self.cardLayout)

        scroll_area.setWidget(scroll_content)

        vbox.addWidget(scroll_area)

#########################################################################

        self.key_listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)
        self.key_listener.start()

        self.setLayout(vbox)
        self.setGeometry(100, 100, 400, 400)
        self.setWindowTitle('PyBot')
        self.show()


    def toggle_randomizer(self, state):
        if state == Qt.CheckState.Checked.value:
            self.randomize = True
        else:
            self.randomize = False

    def change_filename(self, value):
        self.filename = value

    def change_randomizer(self, value):
        try:
            new_randomizer = float(value)
            if new_randomizer < 0:
                raise ValueError()
            self.randomizer = new_randomizer
        except ValueError:
            print('Value is not float >= 1.')
            self.randomizer = 1
            return
    
    def change_speed(self, value):
        try:
            new_speed = float(value)
            if new_speed < 0:
                raise ValueError()
            self.speed = new_speed
        except ValueError:
            print('Value is not positive float.')
            self.speed = 1
            return

    def change_repeat(self, value):
        try:
            new_repeat = int(value)
            self.repeat = new_repeat
        except ValueError:
            print('Value is not positive int.')
            self.repeat = 1
            return


    def toggle_track_move(self, state):
        if state == Qt.CheckState.Checked.value:
            self.track_moving = True
        else:
            self.track_moving = False

    def on_move(self, x, y):
        if self.track_moving and self.recording:
            now = time.time()
            delay = now - self.current_time
            move = [Card.MOVE, delay]
            data = {}
            data['position'] = (x,y)
            move.append(data)
            # self.mouse_events.append(move)
            self.events.append(move)
            self.current_time = now

    def on_click(self, x, y, button, pressed):
        if self.recording:
            now = time.time()
            delay = now - self.current_time
            move = []
            if button == Mouse_Button.left:
                move.append(Card.LEFT_CLICK_PRESS if pressed else Card.LEFT_CLICK_RELEASE)
            elif button == Mouse_Button.right:
                move.append(Card.RIGHT_CLICK_PRESS if pressed else Card.RIGHT_CLICK_RELEASE)
            elif button == Mouse_Button.middle:
                move.append(Card.MIDDLE_CLICK_PRESS if pressed else Card.MIDDLE_CLICK_RELEASE)
            move.append(delay)
            data = {}
            data['position'] = (x,y)
            move.append(data)
            # self.mouse_events.append(move)
            self.events.append(move)
            self.current_time = now

    def on_scroll(self, x, y, dx, dy):
        if self.recording:
            now = time.time()
            delay = now - self.current_time
            move = [Card.SCROLL, delay]
            data = {}
            data['position'] = (x,y)
            data['movement'] = (dx,dy)
            move.append(data)
            # self.mouse_events.append(move)
            self.events.append(move)
            self.current_time = now

    def on_press(self, key):
        if key == keyboard.Key.esc and self.playing:
            self.playing = False
        elif self.recording:
            now = time.time()
            delay = now - self.current_time
            data = {}
            # They way pynput did vk keys doesn't match
            # mac specs and result is some numbers overlap
            # between special keys and normal keys
            try:
                data['vk'] = key.vk
                data['is_media'] = key._is_media
                move = [Card.KEY_PRESS, delay, data]
            except AttributeError:
                data['vk'] = key.value.vk
                data['is_media'] = key.value._is_media
                move = [Card.SPECIAL_KEY_PRESS, delay, data]
            # self.keyboard_events.append(move)
            self.events.append(move)
            self.current_time = now
    
    def on_release(self, key):
        if key == keyboard.Key.esc and self.playing:
            self.playing = False
        elif self.recording:
            now = time.time()
            delay = now - self.current_time
            data = {}
            try:
                data['vk'] = key.vk
                data['is_media'] = key._is_media
                move = [Card.KEY_RELEASE, delay, data]
            except AttributeError:
                data['vk'] = key.value.vk
                data['is_media'] = key.value._is_media
                move = [Card.SPECIAL_KEY_RELEASE, delay, data]
            # self.keyboard_events.append(move)
            self.events.append(move)
            self.current_time = now

    def record(self):
        current = self.record_button.text()
        if current == 'Stop':
            self.record_button.setText('Record')
            self.recording = False
            self.mouse_listener.stop()
            # for event in self.mouse_events[:-2]:
            for event in self.events[:-2]:
                self.addCard(event[0], event[1], event[2])
            
            self.redisplayCards()
        else:
            self.record_button.setText('Stop')
            self.recording = True
            self.cards.clear()
            # self.mouse_events.clear()
            self.events.clear()
            self.keyboard_events.clear()
            self.mouse_listener = mouse.Listener(
                on_move=self.on_move,
                on_click=self.on_click,
                on_scroll=self.on_scroll)
            self.mouse_listener.start()
            self.current_time = time.time()

    def addCard(self, action, delay, data):
        card = QCard(self, action, delay, data)
        self.cards.append(card)

    def play(self):

        mouse = Mouse_Controller()
        keyboard_controller = Keyboard_Controller()

        self.playing = True

        for i in range(self.repeat):
            for card in self.cards:
                action = card.action
                if self.randomize:
                    rand_speed_modifier = random.uniform(1, self.randomizer)
                    if random.random() < 0.5:
                        rand_speed_modifier = 1/rand_speed_modifier
                else:
                    rand_speed_modifier = 1
                wait_time = card.delay / (self.speed * rand_speed_modifier)
                start_time = time.time()
                while time.time() - start_time < wait_time:
                    if not self.playing:
                        return
                if action <= Card.SCROLL: #mouse event
                    mouse.position = card.data['position']
                    if action == Card.MOVE:
                        pass
                    elif action == Card.LEFT_CLICK_PRESS:
                        mouse.press(Mouse_Button.left)
                    elif action == Card.LEFT_CLICK_RELEASE:
                        mouse.release(Mouse_Button.left)
                    elif action == Card.RIGHT_CLICK_PRESS:
                        mouse.press(Mouse_Button.right)
                    elif action == Card.RIGHT_CLICK_RELEASE:
                        mouse.release(Mouse_Button.right)
                    elif action == Card.MIDDLE_CLICK_PRESS:
                        mouse.press(Mouse_Button.middle)
                    elif action == Card.MIDDLE_CLICK_RELEASE:
                        mouse.release(Mouse_Button.middle)
                    elif action == Card.SCROLL:
                        (dx, dy) = card.data['movement']
                        mouse.scroll(dx, dy)
                elif action <= Card.SPECIAL_KEY_RELEASE: #keyboard event
                    if action == Card.KEY_PRESS:
                        keyboard_controller.press(keyboard.KeyCode.from_vk(card.data['vk']))
                    elif action == Card.KEY_RELEASE:
                        keyboard_controller.release(keyboard.KeyCode.from_vk(card.data['vk']))
                    elif action == Card.SPECIAL_KEY_PRESS:
                        if card.data['is_media'] == True:
                            media_key = keyboard.KeyCode._from_media(card.data['vk'])
                            key = keyboard.Key(media_key)
                            print(f'press: {key}')
                            keyboard_controller.press(key)
                        else:
                            keyboard_controller.press(keyboard.KeyCode.from_vk(card.data['vk']))
                    elif action == Card.SPECIAL_KEY_RELEASE:
                        if card.data['is_media'] == True:
                            media_key = keyboard.KeyCode._from_media(card.data['vk'])
                            key = keyboard.Key(media_key)
                            print(f'release : {key}')
                            keyboard_controller.release(key)
                        else:
                            keyboard_controller.release(keyboard.KeyCode.from_vk(card.data['vk']))
                else: # special events: OCR, etc.
                    print('Not implemented yet')
                

    
    def cancelCard(self, card):
        if len(self.cards) > 0:
            # self.cards.pop()
            self.cards.remove(card)
            self.redisplayCards()
    
    def redisplayCards(self):
        for i in reversed(range(self.cardLayout.count())):
            self.cardLayout.itemAt(i).widget().setParent(None)

        for card in self.cards:
            self.cardLayout.addWidget(card)

    def loadFile(self):
        with open(f'./{self.filename}.json', 'r') as file:
            cards = json.load(file)
            for card_data in cards:
                [action, delay, data] = card_data
                action = Card(action)
                card = QCard(self, action, delay, data)
                self.cards.append(card)

        self.redisplayCards()

    def exportFile(self):

        cards = []
        for card in self.cards:
            action = card.action
            delay = card.delay
            data = card.data
            cards.append([action, delay, data])


        with open(f'./{self.filename}.json', 'w') as file:
            json.dump(cards, file)
        

def build():
    app = QApplication(sys.argv)
    
    menu = Menu()

    sys.exit(app.exec())
