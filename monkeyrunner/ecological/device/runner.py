#-*- coding: UTF-8 -*-
"""

"""
import json
import subprocess
import os
import sys
import time
import pymongo
import configparser
import sys
reload(sys)
sys.setdefaultencoding('utf8')
class DeviceRunner():
    _settings = None
    _runner_log = None
    _mongodb_client = None
    def __init__(self,settings):
        self._settings = settings
        config = configparser.ConfigParser()
        config.read("config.ini")
        self._mongodb_client = pymongo.MongoClient(config.get("global", "mongodbip"), 27017)

    def run(self):  # Overwrite run() method, put what you want the thread do here
        print('App(%s), in Device(%s) Time:%s,is running !\n' % (self._settings["categroy"],self._settings["tag"], time.ctime()))
        _tmp_log = self._runner_log
        del _tmp_log
        self._runner_log = {"tag": self._settings["tag"]}
        if self._running() == False:  # 如果设备没有准备好
            return False
        self._write_to_mongodb()  # 将日志写入mongodb
        # self._waitting(self._settings["repeattime"])  # 重启脚本时间间隔，改为由父线程控制
        return True



    # def saveComputer(self, cmd):
    #     screenExecute = subprocess.Popen(str(cmd), stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    #     stdout, stderr = screenExecute.communicate()

    def _running(self):
        # # 打开App
        result = self._launch_app(self._settings["categroy"] + "/" + self._settings["activity"])
        if result !=0:
            return False
        #等待应用启动
        self._waitting(self._settings["setuptime"])
        # 点击
        self._click(self._settings["clickpoint"])
        # 等待数据加载完成
        self._waitting(self._settings["sleeptime"])
        # 下拉以前先记录当前的时间
        self._runner_log["time0"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # 下拉
        self._drag(self._settings["startpoint"], self._settings["endpoint"])
        # 等待数据加载完成
        self._waitting(self._settings["sleeptime"])
        # 截图
        file_name,full_file_name = self._take_photo()
        # 上传图片文件
        self._upload_screenshot(full_file_name)
        self._runner_log["screenshot0"] = file_name
        for i in range(1, 4):
            # 下拉以前先记录当前的时间
            self._runner_log["time"+i] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            # 上拉
            self._dragup(self._settings["startpoint"], self._settings["endpoint"])
            # 等待
            self._waitting(self._settings["sleeptime"])
            # 截图
            file_name, full_file_name = self._take_photo()
            # 上传图片文件
            self._upload_screenshot(full_file_name)
            self._runner_log["screenshot"+i] = file_name
        return True
    #
    # 下面是工具函数
    #
    #结果写入数据库
    def _write_to_mongodb(self):
        db = self._mongodb_client['originnews']
        runner_logs = db["runner_logs"]
        runner_logs.insert(self._runner_log)

    #上传图片文件
    def _upload_screenshot(self,full_file_name):
        cmd = r'curl -F "uploadfile=@'+full_file_name+'" '+self._settings["imgserver"]
        print(cmd)
        response = json.loads(self._execute_cmd(cmd))
        if response["status"] == "success":
            return True
        return False

    def _waitting(self, second):
        # 等待時間
        time.sleep(second)

    def _launch_app(self, apkname):
        # 打开App
        result = os.system("adb -s " +self._settings["tag"]+" shell am start -n " + apkname)
        return result

    def _drag(self, start, end):
        # 下拉刷新
        os.system(
            "adb -s " +self._settings["tag"]+" shell input swipe " + start.split('|')[0] + " " + start.split('|')[1] + " " + end.split('|')[
                0] + " " +
            end.split('|')[1])

    def _dragup(self, end, start):
        # 加载更多
        os.system(
            "adb -s " +self._settings["tag"]+" shell input swipe " + start.split('|')[0] + " " + start.split('|')[1] + " " + end.split('|')[
                0] + " " +
            end.split('|')[1])

    def _click(self, click):
        start,end = click.split('|')
        os.system("adb -s " +self._settings["tag"]+" shell input tap " + start + " " + end)

    #截屏，返回文件名和完整文件路径
    def _take_photo(self):
        # 截图上传
        t = str(int(round(time.time() * 1000)))
        file_name = t + ".png"
        full_file_name = self._cur_file_dir() + "/uploads/" + file_name
        cmd1 = r"adb -s " +self._settings["tag"]+" shell screencap -p /sdcard/" + file_name  # 命令1：在手机上截图
        cmd2 = r"adb -s " +self._settings["tag"]+" pull /sdcard/" + t + ".png " + full_file_name  # 命令2：将图片保存到电脑
        self._execute_cmd(cmd1)  # 在手机上截图
        self._execute_cmd(cmd2)  # 将截图保存到电脑
        return (file_name,full_file_name)

    #执行命令行
    def _execute_cmd(self, cmd):
        screenExecute = subprocess.Popen(str(cmd), stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        stdout, stderr = screenExecute.communicate()

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
        print('Thread Object(%s), Time:%s\n' % (self._settings["tag"], time.ctime()))
