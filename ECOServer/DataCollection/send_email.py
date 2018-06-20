from threading import Thread
import time
import pymysql
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL
from util import *
from pymongo import MongoClient
import datetime

class MongodbConn(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.CONN = MongoClient(ConfigHelper.mongodbip, ConfigHelper.mongodbport)
        self.sdb = pymysql.connect(ConfigHelper.mysql_ip, ConfigHelper.mysql_user,
                                   ConfigHelper.mysql_pwd, ConfigHelper.mysql_db, charset='utf8')
        self.sendemail = "";
    def run(self):
        #连接到mongodb
        database = "crawlnews"
        self.db = self.CONN[database]

        day = time.strftime('%Y%m%d', time.localtime(time.time()))
        # 时间修正一下，改为本地时间
        day = LocalTime.get_local_date(day, "%Y%m%d").strftime("%Y%m%d")
        SingleLogger().log.debug("===tableday====>%s" % day)
        table = self.db["originnews%s" % day]
        #存放每天解析的数据表
        tablelog = self.db["originnewsLog"]
        # mysql使用cursor()方法获取操作游标
        cursor = self.sdb.cursor()
        # 使用execute方法执行SQL语句
        cursor.execute("SELECT * FROM app_information WHERE isartificial = 0")
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
                # 获取当天零点时间
                passtime = day + " %s" % "00:00:00";


                #查询tablelog中数据
                logrows = tablelog.find({"appname": appname,'day': day});
                if logrows.count() == 0:
                    #如果没有数据，插入数据
                    datalog = {'appname':appname,'num':0,'day':day,"time":"00:00:00"}
                    tablelog.insert_one(datalog)
                    logtime = "00:00:00";
                    lognum = 0;
                else:
                    #如果有数据，取出数据
                    logtime = logrows[0]["time"]
                    lognum = logrows[0]["num"]

                # 获取当前的时分秒
                nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                record_date = LocalTime.get_local_date(nowtime, "%Y-%m-%d %H:%M:%S")
                # 时间修正一下，改为本地时间
                nowtime = record_date.strftime("%Y-%m-%d %H:%M:%S")

                # 现在的时分秒
                now = time.strftime('%H:%M:%S', time.localtime(time.time()))
                # 现在的时分秒修正一下，改为本地时间
                now = LocalTime.get_local_date(now, "%H:%M:%S").strftime("%H:%M:%S")
                # 转换成时间戳
                logdaytime = day +" "+ logtime
                nowtimestr = int(time.mktime(time.strptime(nowtime, "%Y-%m-%d %H:%M:%S")))
                logtimestr = int(time.mktime(time.strptime(logdaytime, "%Y-%m-%d %H:%M:%S")))
                # 是否大于70分钟
                if ((nowtimestr - logtimestr)/60) < 70:
                    continue;
                rows = table.find({'crawltimestr': {'$gte': passtime, '$lte': nowtime},"appname": appname}).count();
                if rows == 0:
                    #无数据，记录下来发邮件
                    self.sendemail = self.sendemail + "，%s" % appname
                else:
                    if rows <= int(lognum):
                        #无新数据更新，记录下来发邮件
                        self.sendemail = self.sendemail + "，%s" % appname
                    else:
                        #更新数据
                        tablelog.update({'appname': appname,'day':day}, {'$set': {'num': rows,"time":now}})

                self.i += 1
            if self.sendemail != "":
                self.send(self.sendemail)



    def send(self,appname):
        # qq邮箱smtp服务器
        host_server = 'smtp.qq.com'
        # sender_qq为发件人的qq号码
        sender_qq = '429205398@qq.com'
        # pwd为qq邮箱的授权码
        pwd = 'dpdlgtuuyljwcabc'
        # 发件人的邮箱
        sender_qq_mail = '429205398@qq.com'
        # 收件人邮箱
        receiver = ['zq_li@7coloring.com', '2602306038@qq.com','c_lin@7coloring.com']
        # 邮件的正文内容
        mail_content = '你好%s' % appname + '暂无数据！'
        # 邮件标题
        mail_title = '舆情监控的邮件'

        # ssl登录
        smtp = SMTP_SSL(host_server)
        # set_debuglevel()是用来调试的。参数值为1表示开启调试模式，参数值为0关闭调试模式
        smtp.set_debuglevel(1)
        smtp.ehlo(host_server)
        smtp.login(sender_qq,pwd)

        msg = MIMEText(mail_content, "plain", 'utf-8')
        msg["Subject"] = Header(mail_title, 'utf-8')
        msg["From"] = sender_qq_mail
        msg["To"] = ','.join(receiver)
        smtp.sendmail(sender_qq_mail, receiver, msg.as_string())
        smtp.quit()


if __name__ == '__main__':
    mongo_obj = MongodbConn()
    mongo_obj.run()