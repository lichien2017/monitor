"""

"""
from threading import Thread
import time
class DeviceRunner(Thread):
    tag = "" #对应应用程序的标示，通过这个标示获取脚本和执行频率
    _settings = {}
    def __init__(self,settings):
        Thread.__init__(self)
        self._settings = settings
        self.thread_stop = False

    def run(self):  # Overwrite run() method, put what you want the thread do here
        while not self.thread_stop:
            print('Thread Object(%s), Time:%s\n' % (self.tag,time.ctime()))
            self._running()
            time.sleep(self._settings["repeattime"])

    def stop(self):
        self.thread_stop = True

    def _running(self):
        print('我正在跑')
        # self._launch_app()
        # self._waitting(self._settings["setuptime"])

    # def _launch_app(self):
    #
    #
    def _waitting(self,second):
        time.sleep(second)
    #
    #
    # def _click(self):
    #
    # def _drag(self):
    #
    # def _take_photo(self):
    #
    # def _send_msg(self):

    def to_string(self):
        print('Thread Object(%s), Time:%s\n' % (self.tag, time.ctime()))
