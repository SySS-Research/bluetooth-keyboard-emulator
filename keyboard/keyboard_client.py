#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
  Bluetooth Keyboard Emulator D-Bus Client

  by Matthias Deeg <matthias.deeg@syss.de>, SySS GmbH

  based on BlueZ 5 Bluetooth Keyboard Emulator for Raspberry Pi
  (YAPTB Bluetooth keyboard emulator) by Thanh Le
  Source code and information of this project can be found via
  https://github.com/0xmemphre/BL_keyboard_RPI,
  http://www.mlabviet.com/2017/09/make-raspberry-pi3-as-emulator.html

  MIT License

  Copyright (c) 2018 SySS GmbH
  Copyright (c) 2017 quangthanh010290

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in
  all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
"""

__version__ = '0.8'
__author__ = 'Matthias Deeg'


import dbus
import dbus.service

from pynput import keyboard

# operating modes
NON_INTERACTIVE_MODE = 0
INTERACTIVE_MODE = 1

# USB HID keyboard modifier
MODIFIER_NONE           = 0
MODIFIER_CONTROL_LEFT   = 1 << 0
MODIFIER_SHIFT_LEFT     = 1 << 1
MODIFIER_ALT_LEFT       = 1 << 2
MODIFIER_GUI_LEFT       = 1 << 3
MODIFIER_CONTROL_RIGHT  = 1 << 4
MODIFIER_SHIFT_RIGHT    = 1 << 5
MODIFIER_ALT_RIGHT      = 1 << 6
MODIFIER_GUI_RIGHT      = 1 << 7

# USB HID key codes
KEY_NONE                = 0x00
KEY_A                   = 0x04
KEY_B                   = 0x05
KEY_C                   = 0x06
KEY_D                   = 0x07
KEY_E                   = 0x08
KEY_F                   = 0x09
KEY_G                   = 0x0A
KEY_H                   = 0x0B
KEY_I                   = 0x0C
KEY_J                   = 0x0D
KEY_K                   = 0x0E
KEY_L                   = 0x0F
KEY_M                   = 0x10
KEY_N                   = 0x11
KEY_O                   = 0x12
KEY_P                   = 0x13
KEY_Q                   = 0x14
KEY_R                   = 0x15
KEY_S                   = 0x16
KEY_T                   = 0x17
KEY_U                   = 0x18
KEY_V                   = 0x19
KEY_W                   = 0x1A
KEY_X                   = 0x1B
KEY_Y                   = 0x1C
KEY_Z                   = 0x1D
KEY_1                   = 0x1E
KEY_2                   = 0x1F
KEY_3                   = 0x20
KEY_4                   = 0x21
KEY_5                   = 0x22
KEY_6                   = 0x23
KEY_7                   = 0x24
KEY_8                   = 0x25
KEY_9                   = 0x26
KEY_0                   = 0x27
KEY_RETURN              = 0x28
KEY_ESCAPE              = 0x29
KEY_BACKSPACE           = 0x2A
KEY_TAB                 = 0x2B
KEY_SPACE               = 0x2C
KEY_MINUS               = 0x2D
KEY_EQUAL               = 0x2E
KEY_BRACKET_LEFT        = 0x2F
KEY_BRACKET_RIGHT       = 0x30
KEY_BACKSLASH           = 0x31
KEY_EUROPE_1            = 0x32
KEY_SEMICOLON           = 0x33
KEY_APOSTROPHE          = 0x34
KEY_GRAVE               = 0x35
KEY_COMMA               = 0x36
KEY_PERIOD              = 0x37
KEY_SLASH               = 0x38
KEY_CAPS_LOCK           = 0x39
KEY_F1                  = 0x3A
KEY_F2                  = 0x3B
KEY_F3                  = 0x3C
KEY_F4                  = 0x3D
KEY_F5                  = 0x3E
KEY_F6                  = 0x3F
KEY_F7                  = 0x40
KEY_F8                  = 0x41
KEY_F9                  = 0x42
KEY_F10                 = 0x43
KEY_F11                 = 0x44
KEY_F12                 = 0x45
KEY_PRINT_SCREEN        = 0x46
KEY_SCROLL_LOCK         = 0x47
KEY_PAUSE               = 0x48
KEY_INSERT              = 0x49
KEY_HOME                = 0x4A
KEY_PAGE_UP             = 0x4B
KEY_DELETE              = 0x4C
KEY_END                 = 0x4D
KEY_PAGE_DOWN           = 0x4E
KEY_ARROW_RIGHT         = 0x4F
KEY_ARROW_LEFT          = 0x50
KEY_ARROW_DOWN          = 0x51
KEY_ARROW_UP            = 0x52
KEY_NUM_LOCK            = 0x53
KEY_KEYPAD_DIVIDE       = 0x54
KEY_KEYPAD_MULTIPLY     = 0x55
KEY_KEYPAD_SUBTRACT     = 0x56
KEY_KEYPAD_ADD          = 0x57
KEY_KEYPAD_ENTER        = 0x58
KEY_KEYPAD_1            = 0x59
KEY_KEYPAD_2            = 0x5A
KEY_KEYPAD_3            = 0x5B
KEY_KEYPAD_4            = 0x5C
KEY_KEYPAD_5            = 0x5D
KEY_KEYPAD_6            = 0x5E
KEY_KEYPAD_7            = 0x5F
KEY_KEYPAD_8            = 0x60
KEY_KEYPAD_9            = 0x61
KEY_KEYPAD_0            = 0x62
KEY_KEYPAD_DECIMAL      = 0x63
KEY_EUROPE_2            = 0x64
KEY_APPLICATION         = 0x65
KEY_POWER               = 0x66
KEY_KEYPAD_EQUAL        = 0x67
KEY_F13                 = 0x68
KEY_F14                 = 0x69
KEY_F15                 = 0x6A
KEY_CONTROL_LEFT        = 0xE0
KEY_SHIFT_LEFT          = 0xE1
KEY_ALT_LEFT            = 0xE2
KEY_GUI_LEFT            = 0xE3
KEY_CONTROL_RIGHT       = 0xE4
KEY_SHIFT_RIGHT         = 0xE5
KEY_ALT_RIGHT           = 0xE6
KEY_GUI_RIGHT           = 0xE7

# mapping for special characters (pynput enum values)
KEYMAP_SPECIAL_CHARS = {
    keyboard.Key.alt : (MODIFIER_ALT_LEFT, KEY_NONE),
    keyboard.Key.alt_l : (MODIFIER_ALT_LEFT, KEY_NONE),
    keyboard.Key.alt_r : (MODIFIER_ALT_RIGHT, KEY_NONE),
    keyboard.Key.alt_gr : (MODIFIER_ALT_RIGHT, KEY_NONE),
    keyboard.Key.backspace : (MODIFIER_NONE, KEY_BACKSPACE),
    keyboard.Key.caps_lock : (MODIFIER_NONE, KEY_CAPS_LOCK),
    keyboard.Key.cmd : (MODIFIER_GUI_LEFT, KEY_NONE),
    keyboard.Key.cmd_l : (MODIFIER_GUI_LEFT, KEY_NONE),
    keyboard.Key.cmd_r : (MODIFIER_GUI_RIGHT, KEY_NONE),
    keyboard.Key.ctrl : (MODIFIER_CONTROL_LEFT, KEY_NONE),
    keyboard.Key.ctrl_l : (MODIFIER_CONTROL_LEFT, KEY_NONE),
    keyboard.Key.ctrl_r : (MODIFIER_CONTROL_RIGHT, KEY_NONE),
    keyboard.Key.delete : (MODIFIER_NONE, KEY_DELETE),
    keyboard.Key.down : (MODIFIER_NONE, KEY_ARROW_DOWN),
    keyboard.Key.end : (MODIFIER_NONE, KEY_END),
    keyboard.Key.enter : (MODIFIER_NONE, KEY_RETURN),
    keyboard.Key.esc : (MODIFIER_NONE, KEY_ESCAPE),
    keyboard.Key.f1 : (MODIFIER_NONE, KEY_F1),
    keyboard.Key.f2 : (MODIFIER_NONE, KEY_F2),
    keyboard.Key.f3 : (MODIFIER_NONE, KEY_F3),
    keyboard.Key.f4 : (MODIFIER_NONE, KEY_F4),
    keyboard.Key.f5 : (MODIFIER_NONE, KEY_F5),
    keyboard.Key.f6 : (MODIFIER_NONE, KEY_F6),
    keyboard.Key.f7 : (MODIFIER_NONE, KEY_F7),
    keyboard.Key.f8 : (MODIFIER_NONE, KEY_F8),
    keyboard.Key.f9 : (MODIFIER_NONE, KEY_F9),
    keyboard.Key.f10 : (MODIFIER_NONE, KEY_F10),
    keyboard.Key.f11 : (MODIFIER_NONE, KEY_F11),
    keyboard.Key.f12 : (MODIFIER_NONE, KEY_F12),
    keyboard.Key.f13 : (MODIFIER_NONE, KEY_F13),
    keyboard.Key.f14 : (MODIFIER_NONE, KEY_F14),
    keyboard.Key.f15 : (MODIFIER_NONE, KEY_F15),
    keyboard.Key.home : (MODIFIER_NONE, KEY_HOME),
    keyboard.Key.left : (MODIFIER_NONE, KEY_ARROW_LEFT),
    keyboard.Key.page_down : (MODIFIER_NONE, KEY_PAGE_DOWN),
    keyboard.Key.page_up : (MODIFIER_NONE, KEY_PAGE_UP),
    keyboard.Key.right : (MODIFIER_NONE, KEY_ARROW_RIGHT),
    keyboard.Key.shift : (MODIFIER_SHIFT_LEFT, KEY_NONE),
    keyboard.Key.shift_l : (MODIFIER_SHIFT_LEFT, KEY_NONE),
    keyboard.Key.shift_r : (MODIFIER_SHIFT_RIGHT, KEY_NONE),
    keyboard.Key.space : (MODIFIER_NONE, KEY_SPACE),
    keyboard.Key.tab : (MODIFIER_NONE, KEY_TAB),
    keyboard.Key.up : (MODIFIER_NONE, KEY_ARROW_UP),
    keyboard.Key.insert : (MODIFIER_NONE, KEY_INSERT),
    keyboard.Key.menu : (MODIFIER_GUI_RIGHT, KEY_NONE),
    keyboard.Key.num_lock : (MODIFIER_NONE, KEY_NUM_LOCK),
    keyboard.Key.pause : (MODIFIER_NONE, KEY_PAUSE),
    keyboard.Key.print_screen : (MODIFIER_NONE, KEY_PRINT_SCREEN),
    keyboard.Key.scroll_lock : (MODIFIER_NONE, KEY_SCROLL_LOCK)
}

# key mapping for printable characters of default German keyboard layout
KEYMAP_GERMAN = {
    ' ' : (MODIFIER_NONE, KEY_SPACE),
    '!' : (MODIFIER_SHIFT_LEFT, KEY_1),
    '"' : (MODIFIER_SHIFT_LEFT, KEY_2),
    '#' : (MODIFIER_NONE, KEY_EUROPE_1),
    '$' : (MODIFIER_SHIFT_LEFT, KEY_4),
    '%' : (MODIFIER_SHIFT_LEFT, KEY_5),
    '&' : (MODIFIER_SHIFT_LEFT, KEY_6),
    '(' : (MODIFIER_SHIFT_LEFT, KEY_8),
    ')' : (MODIFIER_SHIFT_LEFT, KEY_9),
    '*' : (MODIFIER_NONE, KEY_KEYPAD_MULTIPLY),
    '+' : (MODIFIER_NONE, KEY_KEYPAD_ADD),
    ',' : (MODIFIER_NONE, KEY_COMMA),
    '-' : (MODIFIER_NONE, KEY_KEYPAD_SUBTRACT),
    '.' : (MODIFIER_NONE, KEY_PERIOD),
    '/' : (MODIFIER_SHIFT_LEFT, KEY_7),
    '0' : (MODIFIER_NONE, KEY_0),
    '1' : (MODIFIER_NONE, KEY_1),
    '2' : (MODIFIER_NONE, KEY_2),
    '3' : (MODIFIER_NONE, KEY_3),
    '4' : (MODIFIER_NONE, KEY_4),
    '5' : (MODIFIER_NONE, KEY_5),
    '6' : (MODIFIER_NONE, KEY_6),
    '7' : (MODIFIER_NONE, KEY_7),
    '8' : (MODIFIER_NONE, KEY_8),
    '9' : (MODIFIER_NONE, KEY_9),
    ':' : (MODIFIER_SHIFT_LEFT, KEY_PERIOD),
    ';' : (MODIFIER_SHIFT_LEFT, KEY_COMMA),
    '<' : (MODIFIER_NONE, KEY_EUROPE_2),
    '=' : (MODIFIER_SHIFT_LEFT, KEY_0),
    '>' : (MODIFIER_SHIFT_LEFT, KEY_EUROPE_2),
    '?' : (MODIFIER_SHIFT_LEFT, KEY_MINUS),
    '@' : (MODIFIER_ALT_RIGHT, KEY_Q),
    'A' : (MODIFIER_SHIFT_LEFT, KEY_A),
    'B' : (MODIFIER_SHIFT_LEFT, KEY_B),
    'C' : (MODIFIER_SHIFT_LEFT, KEY_C),
    'D' : (MODIFIER_SHIFT_LEFT, KEY_D),
    'E' : (MODIFIER_SHIFT_LEFT, KEY_E),
    'F' : (MODIFIER_SHIFT_LEFT, KEY_F),
    'G' : (MODIFIER_SHIFT_LEFT, KEY_G),
    'H' : (MODIFIER_SHIFT_LEFT, KEY_H),
    'I' : (MODIFIER_SHIFT_LEFT, KEY_I),
    'J' : (MODIFIER_SHIFT_LEFT, KEY_J),
    'K' : (MODIFIER_SHIFT_LEFT, KEY_K),
    'L' : (MODIFIER_SHIFT_LEFT, KEY_L),
    'M' : (MODIFIER_SHIFT_LEFT, KEY_M),
    'N' : (MODIFIER_SHIFT_LEFT, KEY_N),
    'O' : (MODIFIER_SHIFT_LEFT, KEY_O),
    'P' : (MODIFIER_SHIFT_LEFT, KEY_P),
    'Q' : (MODIFIER_SHIFT_LEFT, KEY_Q),
    'R' : (MODIFIER_SHIFT_LEFT, KEY_R),
    'S' : (MODIFIER_SHIFT_LEFT, KEY_S),
    'T' : (MODIFIER_SHIFT_LEFT, KEY_T),
    'U' : (MODIFIER_SHIFT_LEFT, KEY_U),
    'V' : (MODIFIER_SHIFT_LEFT, KEY_V),
    'W' : (MODIFIER_SHIFT_LEFT, KEY_W),
    'X' : (MODIFIER_SHIFT_LEFT, KEY_X),
    'Y' : (MODIFIER_SHIFT_LEFT, KEY_Z),
    'Z' : (MODIFIER_SHIFT_LEFT, KEY_Y),
    '[' : (MODIFIER_ALT_RIGHT, KEY_8),
    '\\' : (MODIFIER_ALT_RIGHT, KEY_MINUS),
    ']' : (MODIFIER_ALT_RIGHT, KEY_9),
    '^' : (MODIFIER_NONE, KEY_GRAVE),
    '_' : (MODIFIER_SHIFT_LEFT, KEY_SLASH),
    '`' : (MODIFIER_SHIFT_LEFT, KEY_EQUAL),
    'a' : (MODIFIER_NONE, KEY_A),
    'b' : (MODIFIER_NONE, KEY_B),
    'c' : (MODIFIER_NONE, KEY_C),
    'd' : (MODIFIER_NONE, KEY_D),
    'e' : (MODIFIER_NONE, KEY_E),
    'f' : (MODIFIER_NONE, KEY_F),
    'g' : (MODIFIER_NONE, KEY_G),
    'h' : (MODIFIER_NONE, KEY_H),
    'i' : (MODIFIER_NONE, KEY_I),
    'j' : (MODIFIER_NONE, KEY_J),
    'k' : (MODIFIER_NONE, KEY_K),
    'l' : (MODIFIER_NONE, KEY_L),
    'm' : (MODIFIER_NONE, KEY_M),
    'n' : (MODIFIER_NONE, KEY_N),
    'o' : (MODIFIER_NONE, KEY_O),
    'p' : (MODIFIER_NONE, KEY_P),
    'q' : (MODIFIER_NONE, KEY_Q),
    'r' : (MODIFIER_NONE, KEY_R),
    's' : (MODIFIER_NONE, KEY_S),
    't' : (MODIFIER_NONE, KEY_T),
    'u' : (MODIFIER_NONE, KEY_U),
    'v' : (MODIFIER_NONE, KEY_V),
    'w' : (MODIFIER_NONE, KEY_W),
    'x' : (MODIFIER_NONE, KEY_X),
    'y' : (MODIFIER_NONE, KEY_Z),
    'z' : (MODIFIER_NONE, KEY_Y),
    '{' : (MODIFIER_ALT_RIGHT, KEY_7),
    '|' : (MODIFIER_ALT_RIGHT, KEY_EUROPE_2),
    '}' : (MODIFIER_ALT_RIGHT, KEY_0),
    '~' : (MODIFIER_ALT_RIGHT, KEY_BRACKET_RIGHT),
    u'\'' : (MODIFIER_SHIFT_LEFT, KEY_EUROPE_1),
    u'Ä' : (MODIFIER_SHIFT_LEFT, KEY_APOSTROPHE),
    u'Ö' : (MODIFIER_SHIFT_LEFT, KEY_SEMICOLON),
    u'Ü' : (MODIFIER_SHIFT_LEFT, KEY_BRACKET_LEFT),
    u'ä' : (MODIFIER_NONE, KEY_APOSTROPHE),
    u'ö' : (MODIFIER_NONE, KEY_SEMICOLON),
    u'ü' : (MODIFIER_NONE, KEY_BRACKET_LEFT),
    u'ß' : (MODIFIER_NONE, KEY_MINUS),
    u'€' : (MODIFIER_ALT_RIGHT, KEY_E)
}


class Keyboard():
    """Emulated keyboard"""

    def __init__(self):
        # state structure of the emulated Bluetooth keyboard
        self.state = [
            0xA1,       # input report
            0x01,       # usage report : keyboard
            0x00,       # modifier byte
            0x00,       # Vendor reserved
            0x00,       # 6 bytes for key codes
            0x00,
            0x00,
            0x00,
            0x00,
            0x00]

        self.pressed_key_count = 0              # initialize keypress counter
        self.keymap = KEYMAP_GERMAN             # set keymap
        self.mode = INTERACTIVE_MODE            # interactive mode is default

        # initialize D-Bus client
        print("[*] Initialize D-Bus keyboard client")
        self.bus = dbus.SystemBus()
        self.btkservice = self.bus.get_object("de.syss.btkbdservice",
                                              "/de/syss/btkbdservice")
        self.iface = dbus.Interface(self.btkservice, "de.syss.btkbdservice")

    def change_state(self, keydata, keypress=True):
        """Change keyboard state"""

        print("key count {}".format(self.pressed_key_count))

        if keypress:
            if keydata[0] != MODIFIER_NONE and keydata[1] != KEY_NONE:
                if keydata[1] not in self.state[4:]:
                    # increase key count
                    self.pressed_key_count += 1

                    # find free key slot
                    i = self.state[4:].index(0)

                    # set key
                    self.state[4 + i] = keydata[1]
                    print("Key press {}".format(keydata[1]))

                self.state[2] = keydata[0]


            elif keydata[1] != KEY_NONE:
                if keydata[1] not in self.state[4:]:
                    # increase key count
                    self.pressed_key_count += 1

                    # find free key slot
                    i = self.state[4:].index(0)

                    # set key
                    self.state[4 + i] = keydata[1]
                    print("Key press {}".format(keydata[1]))

            elif keydata[0] != MODIFIER_NONE and keydata[1] == KEY_NONE:
                # process modifier keys
                print("{} pressed".format(keydata[0]))

                self.state[2] |= keydata[0]
                print("Modify modifier byte {}".format(self.state[2]))

        else:
            if keydata[1] != KEY_NONE:
                # decrease keypress count
                self.pressed_key_count -= 1
                print("Key release {}".format(keydata[1]))

                # update state
                i = self.state[4:].index(keydata[1])
                self.state[4 + i] = 0

            if keydata[0] != MODIFIER_NONE:
                print("{} released".format(keydata[0]))
                self.state[2] &= ~keydata[0]

        print(self)
        self.send_input()

    def send_input(self):
        """Forward keyboard events to the D-Bus service"""

        modifier_byte = self.state[2]
        self.iface.send_keys(modifier_byte, self.state[4:10])

    def on_press(self, key):
        """Change keyboard state on key presses"""
        if self.pressed_key_count < 6:
            # set state of newly pressed key but consider limit of max. 6 keys
            # pressed at the same time
            try:
                # process printable characters
                k = self.keymap[key.char]

                # change keyboard state
                self.change_state(k)
            except AttributeError:
                # process special keys
                k = KEYMAP_SPECIAL_CHARS[key]

                # change keyboard state
                self.change_state(k)
            except KeyError:
                print("KeyError: {}".format(key))

    def on_release(self, key):
        """Change keyboard state on key releases"""

        try:
            # process printable characters
            k = self.keymap[key.char]

            # change keyboard state
            self.change_state(k, False)
        except AttributeError:
            # process special keys
            k = KEYMAP_SPECIAL_CHARS[key]

            # change keyboard state
            self.change_state(k, False)
        except KeyError:
            print(key)

        # if key == keyboard.Key.esc:
        #     # Stop listener
        #     return False

    def event_loop(self):
        """Collect events until released"""

        with keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release) as listener:
            listener.join()

    def __str__(self):
        """Keyboard state as string"""

        return repr(self.state)

# main
if __name__ == "__main__":
    print("[*] Intialize keyboard")
    kbd = Keyboard()

    print("[*] Start event loop ...")
    kbd.event_loop()
