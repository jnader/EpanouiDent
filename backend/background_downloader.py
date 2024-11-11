"""
This file contains the QThread responsible for running airmtp
script to retrieve pictures from camera.
"""
import os
from subprocess import run
from PySide6.QtCore import QThread, Signal

class ImageDownloaderThread(QThread):
    download_signal = Signal(str)
    camera_detected = Signal(str)
    error_signal = Signal(str)

    CAMERA_IP = "192.168.1.1"
    DOWNLOAD_DIR = "."
    INTERVAL = 5

    COMMAND = f"--outputdir {DOWNLOAD_DIR} --ifexists uniquename --ipaddress {CAMERA_IP} --realtimedownload only --logginglevel verbose --cameratransferlist exitifnotavail"

    def __init__(self):
        super().__init__()
        self.running = True

    def init_session(self):
        current_file_dir = os.path.sep.join(os.path.abspath(__file__).split(os.path.sep)[:-2])
        dir = os.path.join(current_file_dir, "external", "airmtp", "airnefcmd.py")

        command = f"python3 {dir} {self.COMMAND}"
        with open(".log_airmtp_download", "w") as f:
            run(command.split(" "), stdout=f, stderr=f)

    def run(self):
        self.init_session()

    def stop(self):
        self.running = False
        self.wait()