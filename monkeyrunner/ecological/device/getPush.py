#coding:utf-8

import sys
import time
import re
import unittest
import os
import subprocess
import image
import pymysql
import pymongo
import json
from util.log import Logger
try:
    sys.path.insert(0, os.path.join(os.environ['ANDROID_VIEW_CLIENT_HOME'], 'src'))
except:
    pass

from adbclient import AdbClient
from common import obtainAdbPath

VERBOSE = False
TEST_TEMPERATURE_CONVERTER_APP = False
TEMPERATURE_CONVERTER_PKG = 'com.example.i2at.tc'
TEMPERATURE_CONVERTER_ACTIVITY = 'TemperatureConverterActivity'
CALCULATOR_KEYWORD = 'calculator'
CALCULATOR_ACTIVITY = 'Calculator'

DEBUG = False
DEBUG_SHELL = DEBUG and False

class getPush(unittest.TestCase):
    adbClient = None;
    def __init__(self):
        #adb = obtainAdbPath()
        # 手机唯一标识
        self.deviceTag = 'M3LDU15518000041'
        # try:
        #     self.adbClient = AdbClient(self.deviceTag, settransport=False)
        # except RuntimeError, ex:
        #     if re.search('Connection refused', str(ex)):
        #         raise RuntimeError("adb is not running")
        #     raise (ex)
        phone = r"adb devices -l"
        devices = self._execute_cmd(phone)
        if len(devices) == 0:
            raise RuntimeError("This tests require at least one device connected. None was found.")
        for device in devices:
            if device.status == 'device':
                self.Run()

    def Run(self):
        #mysql
        self.sdb = pymysql.connect("192.168.10.176", "root", "123456", "app_ecological_db", charset='utf8')
        # mysql使用cursor()方法获取操作游标
        cursor = self.sdb.cursor()
        #mongo
        self.CONN = pymongo.MongoClient("192.168.10.176", 27017)
        database = "crawlnews"
        self.db = self.CONN[database]
        table = self.db["push"]

        #获取到通知栏消息
        NotificationList = self.getNotification()
        #数据总数
        NotificationData = NotificationList.split("NotificationRecord")
        for data in NotificationData:
            if data == "":
                return
            else:
                print  >> sys.stderr, "=====>%s" % data
                try:
                    #获取到包名
                    pkgname = data[data.index("pkg"):data.index("user")].replace("pkg=","")
                    print  >> sys.stderr, "pkg=====>%s" % pkgname
                    # 获取到标题
                    title = data[data.index("android.title"):data.index("android.subText")].replace("android.title=", "")
                    print  >> sys.stderr, "title=====>%s" % title
                    # 获取到副标题
                    text = data[data.index("android.text"):data.index("android.progress")].replace("android.text=","")
                    print  >> sys.stderr, "text=====>%s" % text
                    if title !="null" and text!="null":
                        #查询包名的Tag
                        # 使用execute方法执行SQL语句
                        cursor.execute("SELECT * FROM app_information WHERE package = '%s'" % pkgname)
                        # 使用 fetchone() 方法获取一条数据
                        sqldata = cursor.fetchall()
                        if bool(sqldata) != True:
                            print("( ⊙ o ⊙ )啊哦，竟然没有查询到数据结果")
                        else:
                            # 默认下标0为Tag
                            datatag = sqldata[0][0]
                            rows = table.find({"tag":datatag,"title":title,"msg":text}).count();
                            if rows == 0:
                                # 无数据，截图
                                file_name, full_file_name = self._take_photo()
                                # 上传图片文件
                                self._upload_screenshot(full_file_name,file_name)
                                # 获取当前的时分秒
                                nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                                #插入数据库
                                push = {'title': title, 'msg': text, 'tag': datatag,'time':nowtime,'imgfilename':file_name}
                                table.insert_one(push)

                except:
                    print  >> sys.stderr, "=====>err"

    def getNotification(self):
        cmd = r"adb -s '"+self.deviceTag+"' shell dumpsys notification"
        out = str(self._execute_cmd(cmd))
        NotificationList = re.findall("Notification List:(.*)mSoundNotification", out, re.S)[0]
        return NotificationList

    # 截屏，返回文件名和完整文件路径
    def _take_photo(self):
        # 截图上传
        t = str(int(round(time.time() * 1000)))
        day = time.strftime('%Y%m%d', time.localtime(time.time()))
        file_name = day + "_" + t + ".png"
        full_file_name = self._cur_file_dir() + "/uploads/" + file_name
        cmd1 = r"adb -s '"+self.deviceTag+"' shell screencap -p /sdcard/" + file_name  # 命令1：在手机上截图
        cmd2 = r"adb -s '"+self.deviceTag+"' pull /sdcard/" + file_name + " " + full_file_name  # 命令2：将图片保存到电脑
        self._execute_cmd(cmd1)  # 在手机上截图
        self._execute_cmd(cmd2)  # 将截图保存到电脑
        return (file_name, full_file_name)

    # 上传图片文件
    def _upload_screenshot(self, full_file_name,file_name):
        imgserver = "http://192.168.10.176:3000/image"
        cmd = r'curl -F "uploadfile=@' + full_file_name + '" ' + imgserver
        resultOk, error = self._execute_cmd(cmd)
        response = json.loads(resultOk)
        if response["status"] == "success":
            # 删除本地文件
            cmd3 = r'rm -f ' + full_file_name
            # 删除手机文件
            cmd4 = r"adb -s '"+self.deviceTag+"' shell rm /sdcard/"+file_name
            self._execute_cmd(cmd3)
            self._execute_cmd(cmd4)
            return True
        else:
            return False

    #执行命令行
    def _execute_cmd(self, cmd):
        screenExecute = subprocess.Popen(str(cmd), stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        stdout, stderr = screenExecute.communicate()
        return stdout,stderr


    # 获取脚本文件的当前路径
    def _cur_file_dir(self):
        # 获取脚本路径
        path = sys.path[0]
        # 判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
        if os.path.isdir(path):
            return path
        elif os.path.isfile(path):
            return os.path.dirname(path)


if __name__ == '__main__':
    mongo_obj = getPush()
    mongo_obj.run()