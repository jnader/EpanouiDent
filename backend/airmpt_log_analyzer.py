"""
This file contains the QThread responsible for analyzing 
airmtp logs and sending signals to the main thread.
"""
import os
import time
from PySide6.QtCore import QThread, Signal

class AirMTPLogAnalyzer(QThread):
    camera_detected = Signal(str, str)
    download_signal = Signal(str)
    error_signal = Signal(str)

    LOG_FILE = ".log_airmtp_download"

    def __init__(self):
        super().__init__()
        self.running = True
        self.logs_line_count = 0

    def run(self):
        while True:
            time.sleep(3)
            with open(self.LOG_FILE, "r") as f:
                data = f.readlines()
            if data:
                self.latest_logs = "".join(data[self.logs_line_count:]).lower()
                self.logs_line_count += len(data)

                self.analyze_logs()

    def analyze_logs(self):
        """
        Analyze latest logs
        """
        print(self.latest_logs)
        if "camera model" in self.latest_logs:
            data = self.latest_logs.replace("\n", "")
            camera_model = data.split("camera model")[1].split("\"")[1]
            serial_number = data.split("s/n")[-1]
            self.camera_detected.emit(camera_model, serial_number)
        elif "dsc" in self.latest_logs and "100%" in self.latest_logs:
            print("New image received")
        else:
            return

    def stop(self):
        self.running = False
        self.wait()