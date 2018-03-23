"""

"""
from threading import Thread
import time
import subprocess
import os
import sys

class DeviceRunner(Thread):

    _settings = {}
    clickstart = ""

    def __init__(self,settings):
        Thread.__init__(self)
        self._settings = settings
        self.thread_stop = False

    def run(self):  # Overwrite run() method, put what you want the thread do here
        while not self.thread_stop:
            print('Thread Object(%s), Time:%s\n' % (self.tag, time.ctime()))
            self._launch_app(self._settings["categroy"]+"/"+self._settings["activity"])
            self._waitting(self._settings["setuptime"])
            self._running()
            self._waitting(self._settings["setuptime"])

    def _waitting(self, second):
        # 等待時間
        time.sleep(second)

    def _launch_app(self, apkname):
        # 打开App
        os.system("adb shell am start -n " + apkname)

    def _drag(self, start, end):
        # 下拉刷新
        os.system(
            "adb shell input swipe " + start.split('|')[0] + " " + start.split('|')[1] + " " + end.split('|')[0] + " " +
            end.split('|')[1])

    def _dragup(self, end, start):
        # 加载更多
        os.system(
            "adb shell input swipe " + start.split('|')[0] + " " + start.split('|')[1] + " " + end.split('|')[0] + " " +
            end.split('|')[1])

    def _click(self, click):
        # 点击
        if self.clickstart == "":
            self.clickstart = str(int(click.split('|')[0]) + 100)
        else:
            self.clickstart = str(int(self.clickstart) + 100)

        os.system("adb shell input tap " + self.clickstart + " " + click.split('|')[1])

    def _take_photo(self):
        # 截图上传
        t = str(int(round(time.time() * 1000)))
        file_name = t + ".png"
        full_file_name = self._cur_file_dir()+"/uploads/" + file_name
        cmd1 = r"adb shell screencap -p /sdcard/" + file_name      # 命令1：在手机上截图
        cmd2 = r"adb pull /sdcard/" + t + ".png "+ full_file_name  # 命令2：将图片保存到电脑
        self._execute_cmd(cmd1) # 在手机上截图
        self._execute_cmd(cmd2) # 将截图保存到电脑

    def _execute_cmd(self, cmd):
        screenExecute = subprocess.Popen(str(cmd), stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        stdout, stderr = screenExecute.communicate()

    # def saveComputer(self, cmd):
    #     screenExecute = subprocess.Popen(str(cmd), stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    #     stdout, stderr = screenExecute.communicate()

    def _running(self):
        # # 打开App
        # self._launch_app()
        # 下拉
        self._drag(self._settings["startpoint"], self._settings["endpoint"])
        # 等待
        self._waitting(self._settings["repeattime"])
        # 截图
        self._take_photo()
        for i in range(1, 4):
            # 上拉
            self._dragup(self._settings["startpoint"], self._settings["endpoint"])
            # 等待
            self._waitting(self._settings["repeattime"])
            # 截图
            self._take_photo()
        # 点击
        self._click(self._settings["clickpoint"])

    # 获取脚本文件的当前路径
    def _cur_file_dir(self):
        # 获取脚本路径
        path = sys.path[0]
        # 判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
        if os.path.isdir(path):
            return path
        elif os.path.isfile(path):
            return os.path.dirname(path)

    def to_string(self):
        print('Thread Object(%s), Time:%s\n' % (1, time.ctime()))
