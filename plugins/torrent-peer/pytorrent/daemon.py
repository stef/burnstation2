import subprocess
import os
import signal
import time

class Daemon(object):
    term = signal.SIGTERM
    kill = signal.SIGKILL
    
    def __init__(self, executable):
        self.executable = executable
        self.pid = None
        self.process = None
        
    def start(self):
        self.process = subprocess.Popen(self.executable)
        self.pid = self.process.pid
        
    def stop(self):
        if self.process:
            pid = self.process.pid
            
            for i in range(0, 10):
                if self.process.poll() is not None:
                    return
                os.kill(pid, self.term)
                time.sleep(0.1)
                
            for i in range(0, 10):
                if self.process.poll() is not None:
                    return
                os.kill(pid, self.kill)
                time.sleep(0.1)
