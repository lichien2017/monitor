from threading import Thread
from util import *
import sys
from pymongo import MongoClient
import requests
import os.path
import time
import pymysql
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL

class MongodbConn():

    def __init__(self):
        Thread.__init__(self)
        self.count = 0
        self.CONN = MongoClient(ConfigHelper.mongodbip, ConfigHelper.mongodbport)
        self.sdb = pymysql.connect(ConfigHelper.mysql_ip, ConfigHelper.mysql_user,
                                  ConfigHelper.mysql_pwd, ConfigHelper.mysql_db, charset='utf8')




    def run(self):
        # 连接到mongodb
        database = "crawlnews"
        self.db = self.CONN[database]
        tablelog = self.db["update_app"]
        datarow = tablelog.find({"updateflag":1});
        for row in datarow:
              updatetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
              # 时间修正一下，改为本地时间
              updatetime = LocalTime.get_local_date(updatetime, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
              # 使用adb方法更新软件
              # 查询这个App属于的手机编码
              # mysql使用cursor()方法获取操作游标
              cursor = self.sdb.cursor()
              # 使用execute方法执行SQL语句
              cursor.execute("SELECT * FROM crawl_runner WHERE app_tag='%s'" % row["apptag"])
              # 使用 fetchone() 方法获取一条数据
              data = cursor.fetchall()
              if bool(data) != True:
                  print("( ⊙ o ⊙ )啊哦，竟然没有查询到数据结果")
              else:
                  # 每一条对应的设备号是一样的，所以只取第一条
                  sqldata = data[0]
                  # 默认下标1为设备号
                  devices = sqldata[15]
                  # adb方式安装软件(需要设备号，文件路径)
                  adb = "adb -s %s install -r %s" %(devices,row["full_file_name"])
                  os.system(adb)
                  # 更改更新字段（0：不需要更新 1：需要更新）
                  tablelog.update({'url': row["url"]}, {'$set': {"updateflag":0,"updatetime":updatetime}})

if __name__ == '__main__':
    mongo_obj = MongodbConn()
    mongo_obj.run()