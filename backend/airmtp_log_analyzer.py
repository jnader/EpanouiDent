"""
This file contains the QThread responsible for analyzing
airmtp logs and sending signals to the main thread.
"""
import os
import time
from PySide6.QtCore import QThread, Signal

class AirMTPLogAnalyzer(QThread):
    camera_detected = Signal(str, str)
    camera_disconnected = Signal(bool)
    download_signal = Signal(str)
    error_signal = Signal(str)

    LOG_FILE = ".log_airmtp_download"

    def __init__(self):
        super().__init__()
        self.running = True
        self.logs_line_count = 0
        self.camera_detected_flag = False

    def run(self):
        while True:
            time.sleep(3)
            with open(self.LOG_FILE, "r") as f:
                data = [line.rstrip("\n") for line in f.readlines()]
            if data and len(data) > self.logs_line_count:
                self.latest_logs = "".join(data[self.logs_line_count:])
                self.logs_line_count = len(data)

                self.analyze_logs()

    def analyze_logs(self):
        """
        Analyze latest logs.
        TODO: use regex and maybe analyze logs line by line
        """
        if "Camera Model" in self.latest_logs:
            # TODO: Replace with regexp
            camera_model = self.latest_logs.split("Camera Model")[1].split("\"")[1]
            serial_number = self.latest_logs.split("S/N")[-1].split("\"")[1]
            self.camera_detected.emit(camera_model, serial_number)
            self.camera_detected_flag = True
        elif "DSC" in self.latest_logs and "[size = " in self.latest_logs:
            downloaded_file_path = self.latest_logs.split("[size = ")[0].split("100%")[-1].replace(" ", "")
            self.download_signal.emit(downloaded_file_path)
        elif "Delaying 5 seconds before retrying" in self.latest_logs and self.camera_detected_flag:
            self.camera_detected_flag = False
            self.camera_disconnected.emit(True)
        else:
            return

    def stop(self):
        self.running = False
        self.wait()