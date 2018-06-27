from screencap.screencap_match import ScreenCaptureMatch
from util import *
class ScreenCaptureMatchRecv(ScreenCaptureMatch):
    def run(self):
        while not self.thread_stop:
            self.recv_data()
            SingleLogger().log.debug("ScreenCaptureMatchRecv sleep")

    pass