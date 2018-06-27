from screencap.screencap_match import ScreenCaptureMatch
from util import *
class ScreenCaptureMatchSendData(ScreenCaptureMatch):
    def run(self):
        while not self.thread_stop:
            self.send_data()
            SingleLogger().log.debug("ScreenCaptureMatchSendData sleep")
    pass