from pynput import keyboard
from pynput.keyboard import Key
from pynput.keyboard import Controller

c = Controller()

# c.press(keyboard.KeyCode.from_vk(7))
# c.press(keyboard.Key.media_volume_mute)

desired = keyboard.Key.media_volume_mute
print(desired)
print(type(desired))
print(f'{desired.name} : {desired.value}')
print(type(desired.value))

a = keyboard.KeyCode._from_media(7)
test = keyboard.Key(a)
print(test)