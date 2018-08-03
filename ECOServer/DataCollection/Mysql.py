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
                                  ConfigHelper.mysql_pwd, ConfigHelper.mysql_db, charset='utf8mb4')
    def run(self):
        # 获取前一天的日期
        yestoday_str = LocalTime.yestoday_str("%Y%m%d")
        # mysql使用cursor()方法获取操作游标
        cursor = self.sdb.cursor()
        # 应该取的是前一天的月份，不然跨月会错误
        month =  LocalTime.yestoday_str("%Y%m")
        monthtable = "ResDataMonth%s" % month
        # 查找数据库是否有本月的表
        try:
            # 使用execute方法执行SQL语句
            cursor.execute("SELECT * FROM %s" % monthtable)
        except:
            # 没有表执行创建新表方法
            createsql= self.createsql(monthtable)
            cursor.execute(createsql)
            self.sdb.commit()
        # 将昨天的数据导入MySQL中
        # 连接到mongodb
        database = "crawlnews"
        self.db = self.CONN[database]
        table = self.db["originnews%s" % yestoday_str]
        # passtime = '2018-07-08 19:07:36'
        # nowtime = '2018-07-08 23:59:59'
        #找出匹配上的数据
        # datarow = table.find({'crawltimestr': {'$gte': passtime, '$lte': nowtime}})
        datarow = table.find()
        for row in datarow:
            sqlid = "SELECT * FROM %s WHERE identity='%s'" % (monthtable, row["identity"])
            cursor.execute(sqlid)
            data = cursor.fetchall()
            if bool(data) != True:
                # MySQL中无数据
                # 查询screencapocr中有没有数据
                screencapocrtable = self.db["screencapocr%s" % yestoday_str]
                screencapocrrow = screencapocrtable.find({"res_id":row["identity"]})
                imgfilename = ""
                if screencapocrrow.count() != 0:
                    imgfilename = screencapocrrow[0]["image"]
                if row["restype"] == 4:
                    imgfilename = row["gallary"]
                title = row["title"]
                content = row["content"]
                content.replace("<P>", "")
                # mongodb取出数据拼接写入MySql
                insertsql = self.insertsql(monthtable,row["title"],row["description"],content,row["source"],row["pubtimestr"],row["pubtime"],
                           row["crawltimestr"],row["crawltime"],row["status"],row["shorturl"],row["logo"],row["labels"],
                           row["keyword"],row["seq"],row["identity"],row["appname"],row["app_tag"],row["category_tag"],
                           row["category"],row["restype"],row["gallary"],row["video"],row["audio"],imgfilename)
                try:
                    cursor.execute(insertsql)
                    self.sdb.commit()
                except Exception as e:
                    SingleLogger().log.error("======error=======>%s" % e)
                    SingleLogger().log.error("=======title======>%s"% title)
                    SingleLogger().log.error("=======content======>%s" % content)



    def insertsql(self,monthtable,title,description,content,source,pubtimestr,pubtime,crawltimestr,crawltime,status,shorturl,logo,
                        labels,keyword,seq,identity,appname,app_tag,category_tag,category,restype,gallary,video,audio,imgfilename):
        sql = "INSERT INTO %s (title,description,content,source,pubtimestr,pubtime,crawltimestr,crawltime,status,shorturl,logo," \
              "labels,keyword,seq,identity,appname,app_tag,category_tag,category,restype,gallary,video,audio,imgfilename) VALUES" \
              "('%s', '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" \
              % (monthtable,pymysql.escape_string(title),pymysql.escape_string(description), pymysql.escape_string(content),source,pubtimestr,pubtime,
                 crawltimestr,crawltime,status,shorturl,logo,labels,keyword,seq,identity,appname,app_tag,category_tag,category,restype,gallary,video,audio,imgfilename)
        return sql



    def createsql(self,month):
        sql="CREATE TABLE `%s` (`id` int(11) NOT NULL AUTO_INCREMENT," \
                "`title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL," \
                "`description` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL," \
                "`content` text COLLATE utf8mb4_general_ci DEFAULT NULL," \
                "`source` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL," \
                "`pubtimestr` datetime DEFAULT NULL,`pubtime` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL," \
                "`crawltimestr` datetime NOT NULL,`crawltime` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL," \
                "`status` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL," \
                "`shorturl` text COLLATE utf8mb4_general_ci DEFAULT NULL," \
                "`logo` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL," \
                "`labels` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL," \
                "`keyword` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL," \
                "`seq` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL," \
                "`identity` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL," \
                "`appname` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL," \
                "`app_tag` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL," \
                "`category_tag` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL," \
                "`category` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL," \
                "`restype` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL," \
                "`gallary` text COLLATE utf8mb4_general_ci DEFAULT NULL," \
                "`video` text COLLATE utf8mb4_general_ci DEFAULT NULL," \
                "`audio` text COLLATE utf8mb4_general_ci DEFAULT NULL," \
                "`imgfilename` text COLLATE utf8mb4_general_ci DEFAULT NULL," \
                "PRIMARY KEY (`id`),KEY `title` (`title`),KEY `crawltimestr` (`crawltimestr`),KEY `app_tag` (`app_tag`)," \
                "KEY `appname` (`appname`),KEY `identity` (`identity`),KEY `pubtimestr` (`pubtimestr`)) ENGINE=InnoDB DEFAULT " \
                "CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci" % month
        return sql



if __name__ == '__main__':
    mongo_obj = MongodbConn()
    mongo_obj.run()