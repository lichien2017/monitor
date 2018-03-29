#coding:utf-8

import sys
import time
import re
import unittest
import os
import subprocess
import image
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

class AdbClientTest(unittest.TestCase):
    adbClient = None;
    def __init__(self):
        adb = obtainAdbPath()
        # we use 'fakeserialno' and settransport=False so AdbClient does not try to find the
        # serialno in setTransport()
        try:
            self.adbClient = AdbClient('M3LDU15518000041', settransport=False)
        except RuntimeError, ex:
            if re.search('Connection refused', str(ex)):
                raise RuntimeError("adb is not running")
            raise (ex)
        devices =  self.adbClient.getDevices()
        if len(devices) == 0:
            raise RuntimeError("This tests require at least one device connected. None was found.")
        for device in devices:
            if device.status == 'device':
                androidSerial = device.serialno
                print(androidSerial)
                self.StartActivity()
                time.sleep(10)
                self.Run()

    def Run(self):
        #下拉
        self.adbClient.drag((520,520),(520,1220),100)
        #暂停
        time.sleep(10)
        #拍照
        self._take_photo()
        #暂停
        time.sleep(5)
        for i in range(1, 4):
            #上拉
            self.adbClient.drag((520,1220),(520,520),100)
            #暂停
            time.sleep(5)
            # 拍照
            self._take_photo()
        # 点击
        self.adbClient.touch(220, 270, 100)

    def _take_photo(self):
        image = self.adbClient.takeSnapshot()
        t = str(int(round(time.time() * 1000)))
        file_name = t + ".png"
        full_file_name = self._cur_file_dir() + "/uploads/" + file_name
        image.save(full_file_name)

    def StartActivity(self):
        self.adbClient.startActivity('com.ss.android.article.news' + '/.' + 'activity.SplashActivity')

    # 获取脚本文件的当前路径
    def _cur_file_dir(self):
        # 获取脚本路径
        path = sys.path[0]
        # 判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
        if os.path.isdir(path):
            return path
        elif os.path.isfile(path):
            return os.path.dirname(path)


testadb = AdbClientTest()