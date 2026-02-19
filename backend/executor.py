import subprocess
import threading
import queue

class InteractiveExecutor:
    def __init__(self, code):
        self.process = subprocess.Popen(
            ["python3", "-u", "-c", code],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        self.output_queue = queue.Queue()

        def read_output():
            if self.process.stdout:
                for line in self.process.stdout:
                    self.output_queue.put(line)

        threading.Thread(target=read_output, daemon=True).start()

    def write(self, data):
        if self.process.stdin:
            self.process.stdin.write(data)
            self.process.stdin.flush()

    def read(self):
        output = ""
        while not self.output_queue.empty():
            output += self.output_queue.get()
        return output
