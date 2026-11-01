import pyperclip, datetime, time, threading, ast

class Cliplogger:
    def __init__(self):
        self.last = ""
        self.history = []
        self.is_running = False
        self.current_val = None
        self.date = None
        self.thread = None

    def start_cliplog(self):
        if self.is_running:
            self.is_running = False
        self.is_running = True

        self.thread = threading.Thread(target=self._monitor_clipboard_, daemon=True)
        self.thread.start()

    def _monitor_clipboard_(self):
        while self.is_running:
            try:
                self.date = datetime.datetime.now()
                self.current_val = pyperclip.paste()
                if self.current_val and self.current_val != self.last:
                    clean = self.current_val.replace("\r\n", "\n")
                    self.history.append(f"[{self.date}] :: {clean}")
                    self.last = self.current_val
                time.sleep(0.5)
            except Exception as e:
                pass

    def read_cliplog(self):
        return self.history

    def stop_cliplog(self):
        if self.is_running:
            self.is_running = False
            self.current_val = None

    def wrap_read_cliplog(self):
        logs = self.read_cliplog()
        out = ""
        for item in logs:
            if " :: " in item:
                timestamp, content = item.split(" :: ", 1)

                if content.startswith("[") and content.endswith("]"):
                    try:
                        content_list = ast.literal_eval(content)
                        content = "\n".join([str(x).strip() for x in content_list if x])
                    except Exception:
                        pass
                clean_content = content.replace("\r\n", "\n").strip()
                out += "-"*50 + "\n" + f"({timestamp}) :: \n{clean_content}\n" + "-"*50 + "\n"
            else:
                out += item.replace("\r\n", "\n") + "\n" + "-"*50 + "\n"
        return out