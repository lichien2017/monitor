import pymongo
from threading import Thread
import time
from util import *
import pymysql
from util import LocalTime
from pymongo import MongoClient


class MongodbConn(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.CONN = MongoClient(ConfigHelper.mongodbip, ConfigHelper.mongodbport)
        self.sdb = pymysql.connect(ConfigHelper.mysql_ip, ConfigHelper.mysql_user,
                                  ConfigHelper.mysql_pwd, ConfigHelper.mysql_db, charset='utf8')
    def run(self):
        #连接到mongodb
        database = "crawlnews"
        self.db = self.CONN[database]
        day = time.strftime('%Y%m%d', time.localtime(time.time()))
        # 时间修正一下，改为本地时间
        day = LocalTime.get_local_date(day, "%Y%m%d").strftime("%Y%m%d")
        table = self.db["originnews%s" % day]
        # mysql使用cursor()方法获取操作游标
        cursor = self.sdb.cursor()
        # 使用execute方法执行SQL语句
        cursor.execute("SELECT * FROM app_information  WHERE isartificial = 0")
        # 使用 fetchone() 方法获取一条数据
        data = cursor.fetchall()
        if bool(data) != True:
            print("( ⊙ o ⊙ )啊哦，竟然没有查询到数据结果")
        else:
            # 对查询出的数据进行处理
            self.i = 0;
            for record in data:
                sqldata = data[self.i]
                #默认下标1为应用名
                appname = sqldata[1]
                #获取当前日期





                day = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                # 时间修正一下，改为本地时间
                day = LocalTime.get_local_date(day, "%Y-%m-%d").strftime("%Y-%m-%d")
                #获取当前的时分秒
                nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                record_date = LocalTime.get_local_date(nowtime, "%Y-%m-%d %H:%M:%S")
                # 时间修正一下，改为本地时间
                nowtime = record_date.strftime("%Y-%m-%d %H:%M:%S")


                #获取当天零点时间
                passtime = day + " %s" % "00:00:00";
                rows = table.find({'crawltimestr': {'$gte': passtime, '$lte': nowtime},"appname": appname}).count();
                print(appname + "==========>%s" % rows)
                self.i += 1

if __name__ == '__main__':
    mongo_obj = MongodbConn()
    mongo_obj.run()