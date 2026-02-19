import os
import pty
import subprocess
import select

class InteractiveExecutor:
    def __init__(self, code):
        self.master, self.slave = pty.openpty()

        self.process = subprocess.Popen(
            ["python3", "-u", "-c", code],
            stdin=self.slave,
            stdout=self.slave,
            stderr=self.slave,
            close_fds=True
        )

    def write(self, data):
        os.write(self.master, data.encode())

    def read(self):
        output = ""
        while True:
            r, _, _ = select.select([self.master], [], [], 0.1)
            if self.master in r:
                try:
                    data = os.read(self.master, 1024).decode()
                    output += data
                except OSError:
                    break
            else:
                break
        return output