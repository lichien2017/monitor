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

class AppDown(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.count = 0
        self.CONN = MongoClient(ConfigHelper.mongodbip, ConfigHelper.mongodbport)
        self.sdb = pymysql.connect(ConfigHelper.mysql_ip, ConfigHelper.mysql_user,
                                  ConfigHelper.mysql_pwd, ConfigHelper.mysql_db, charset='utf8')
        self.sendemail = "";



    def run(self):
        # 连接到mongodb
        database = "crawlnews"
        self.db = self.CONN[database]
        tablelog = self.db["update_app"]
        dataUrl = tablelog.find();
        for url in dataUrl:
           #根据网址下载到本地
           dicts = self.download_apk(url["url"])
           updatetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
           # 时间修正一下，改为本地时间
           updatetime = LocalTime.get_local_date(updatetime, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
           # 拆分字符串获取信息
           # 文件大小
           filesize = dicts[1]
           # 文件路径
           full_file_name = dicts[2]
           # 大小不同需要更新
           if filesize != url["filesize"]:
              # 记录一下准备发送邮件
              self.sendemail = self.sendemail + "，%s" % url["appname"]
              # 更改更新字段（默认为0：不需要更新 1：需要更新）
              tablelog.update({'url': url["url"]},
                              {'$set': {'filesize': filesize, "time": updatetime, "full_file_name": full_file_name,"updateflag":1}})
        if self.sendemail != "":
            self.send(self.sendemail)

    def send(self, appname):
        # qq邮箱smtp服务器
        host_server = 'smtp.qq.com'
        # sender_qq为发件人的qq号码
        sender_qq = '429205398@qq.com'
        # pwd为qq邮箱的授权码
        pwd = 'dpdlgtuuyljwcabc'
        # 发件人的邮箱
        sender_qq_mail = '429205398@qq.com'
        # 收件人邮箱
        receiver = ['zq_li@7coloring.com', '2602306038@qq.com', 'c_lin@7coloring.com']
        # 邮件的正文内容
        mail_content = '你好%s' % appname + '需要更新！'
        # 邮件标题
        mail_title = '舆情软件更新的邮件'

        # ssl登录
        smtp = SMTP_SSL(host_server)
        # set_debuglevel()是用来调试的。参数值为1表示开启调试模式，参数值为0关闭调试模式
        smtp.set_debuglevel(1)
        smtp.ehlo(host_server)
        smtp.login(sender_qq, pwd)

        msg = MIMEText(mail_content, "plain", 'utf-8')
        msg["Subject"] = Header(mail_title, 'utf-8')
        msg["From"] = sender_qq_mail
        msg["To"] = ','.join(receiver)
        smtp.sendmail(sender_qq_mail, receiver, msg.as_string())
        smtp.quit()






    # 获取脚本文件的当前路径
    def _cur_file_dir(self):
        # 获取脚本路径
        path = sys.path[0]
        # 判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
        if os.path.isdir(path):
            return path
        elif os.path.isfile(path):
            return os.path.dirname(path)

    def download_apk(self,url):
           """
           下载文件
           :param url:下载链接
           :param num:索引值
           """
           global count
           succeed = 'Succeed'
           failure = 'Failure'
           print('url:\n' + url)
           response = requests.head(url)

           try:
               url = response.headers['Location']
               b = str(url).index(".apk") + 4
               url = str(url)[0:b]
               filename = os.path.basename(url)
               filename = filename.split('?')[0]
               response = requests.head(url)
               filesize = round(float(response.headers['Content-Length']) / 1048576, 2)
           except:
               SingleLogger().log.debug("无法获取真实下载地址")
               return
           # apk_format = 'application/vnd.android.package-archive'
           # apk_format = 'application/octet-stream'



           # 过滤非zip文件或大于100.00M的文件
           # TODO 可按需修改
           # response.headers['Content-Type'] == apk_format and filesize < 100.00
           if filesize < 100.00:
               # 下载文件
               headers = {
                   'User-Agent': 'Mozilla/5.0 (Linux; U; Android 4.0.3; zh-cn; M032 Build/IML74K) '
                                 'AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
                   'Connection': 'keep-alive', }
               file = requests.get(url, headers=headers, timeout=10)
               full_file_name = self._cur_file_dir() + "/uploads/" + filename
               with open(full_file_name, 'wb') as apk:
                   apk.write(file.content)
                   print(succeed + "\n")
                   self.count += 1

               # 返回内容
               dicts = [url, str(filesize), full_file_name]
               return dicts
           else:
               print('文件类型:' + response.headers['Content-Type'] + "\n" +
                     '文件大小:' + str(filesize) + 'M' + "\n" +
                     failure + "\n")
               dicts = [url, failure, failure]
               return dicts


if __name__ == '__main__':
    down_obj = AppDown()
    down_obj.run()