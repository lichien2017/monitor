# coding=utf-8
import redis
import json
import threadpool
import sys
from time import sleep
from pymongo import MongoClient
from util import *
from bs4 import BeautifulSoup
# log = Logger()
#消息队列
class MyQueue(object):
    def __init__(self,db=7, host='localhost'):
        self.rcon = redis.Redis(host=host, port=ConfigHelper.redisport, db=db)
        #print("db is:",db)
        # self.queue = queuename

    def pop(self, queuename):
        obj = self.rcon.rpop(queuename)
        return obj

    def push(self, queuename, obj):
        self.rcon.lpush(queuename, obj)

#解析基类
class BaseParse(object):
    def __init__(self,name,appname,apptag,categroytag):
        self.name = name
        self.appname = appname
        self.apptag = apptag
        self.categroytag = categroytag
        print(name)

    #插入mongodb
    def db(self,sdata,articleid,title):
        conn = MongoClient(ConfigHelper.mongodbip, ConfigHelper.mongodbport)
        SingleLogger().log.debug("save db1 %s" % articleid)
        # 待插入数据的时期
        record_date = LocalTime.get_local_date(sdata["crawltimestr"],"%Y-%m-%d %H:%M:%S")
        pub_date = LocalTime.get_local_date(sdata["pubtimestr"], "%Y-%m-%d %H:%M:%S")
        SingleLogger().log.debug("save db2 %s" % articleid)
        record_date_utc = sdata["crawltimestr"]
        # 时间修正一下，改为本地时间
        sdata["crawltimestr"] = record_date.strftime("%Y-%m-%d %H:%M:%S")
        sdata["pubtimestr"]= pub_date.strftime("%Y-%m-%d %H:%M:%S")
        SingleLogger().log.debug("save db3 %s" % articleid)
        db = conn["crawlnews"]  #连接crawlnews数据库 ,这里按月来分库
        my_originnews = db["originnews"+record_date.strftime("%Y%m%d")]  # lzq 修改，把数据存入每天的分表
        SingleLogger().log.debug("save db4 %s" % "originnews"+record_date.strftime("%Y%m%d"))
        #查询是否存在此唯一标识的数据
        artcount= my_originnews.find({"identity": str(articleid)}).count()
        if artcount>0:
            SingleLogger().log.debug("有相同的id数据=%s" % articleid)
            sdata['identity']=genearteMD5(title+str(articleid))
            #查询是否存在此标题的数据
            titlecount= my_originnews.find({"title": str(title)}).count()
            if titlecount>0:
                SingleLogger().log.debug("有相同的title数据=%s" % title)
                return
        #插入数据库
        SingleLogger().log.debug("save db5 %s" % "originnews" + record_date.strftime("%Y%m%d"))
        try:
            my_originnews.save(sdata)
        except Exception as ex :
            SingleLogger().log.error(ex)
        else:
            # 把数据分发给打标服务，服务分为两类，一类基础服务（0），一类高级服务（1）
            # 数据包里面要包含标示和日期，所以要重新构建包 lzq
            msg = {"res_id":"%s"%articleid,"time":LocalTime.get_local_date(record_date_utc,"%Y-%m-%d %H:%M:%S").strftime("%Y%m%d"),
                   "record_time":"%s" % sdata["crawltimestr"]}
            SingleLogger().log.debug("Rule0server.execute_all == %s",json.dumps(msg))
            Rule0server.execute_all(json.dumps(msg)) # 插入的数据格式为json
            # SingleLogger().log.debug("Rule1server.add_resource_to_all_queue == %s", json.dumps(msg))
            # Rule1server.add_resource_to_all_queue(json.dumps(msg))
            #分发给下载资源服务
            queue = MyQueue(db=ConfigHelper.redisdb, host=ConfigHelper.redisip)
            queue.push(ConfigHelper.download_msgqueue,json.dumps(msg))
    #每个App解析方法重载该方法
    def tryparse(self,str):
        None
    # 获取html中的图片列表
    def getHtmlImages(self,url):
        # html = rq.get(urls).text
        html = Http.get(url)
        soup = BeautifulSoup(html, "html.parser")  # 文档对象
        imgStr = ""
        for k in soup.find_all('img'):  # 获取img
            imgStr += k['src'] + ","
        return imgStr

    # 获取html的body内容
    def getHtmlBody(self,url):
        # html = rq.get(urls).text
        html = Http.get(url)
        soup = BeautifulSoup(html, "html.parser")  # 文档对象
        # imgStrArr = soup.find_all('div', class_="Nfgz6aIyFCi3vZUoFGKEr")
        body = soup.find('body')
        # print(len(imgStrArr))
        if body == None :
            return ''
        else:
            return body

    # 获取html中的视频列表
    def getHtmlVideos(self,url):
        # html = rq.get(urls).text
        html = Http.get(url)
        soup = BeautifulSoup(html, "html.parser")  # 文档对象
        imgStr = ""
        for k in soup.find_all('video'):
            imgStr += k['src'] + ","
        return imgStr
#生成md5
def genearteMD5(strs):
    return Secret.md5(strs)

#解析框架，做为线程池的处理函数流程
#1、创建解析对象
#2、读取对应消息队列，没有则跳出
#3、解析
#4、入库
def flowparse(confdata):
    #create BaseParse by reflact
    #parser = BaseParse(confdata["parsername"])
    # confdata = confobj["conf"]
    #log.debug('the confdata is:', confdata)

    amod = __import__(confdata["modname"], fromlist=True)
    #amod = __import__("ToutiaoModel", fromlist=True)
    #log.debug('imported modname')
    aclass = getattr(amod, confdata["classname"])
    parser = aclass(confdata["classname"],confdata["apppinfo"]["app_name"],confdata["apppinfo"]["app_tag"],confdata["apppinfo"]["categroy"])

    #log.debug('created confdata')
    queue = MyQueue(db=ConfigHelper.redisdb,host=ConfigHelper.redisip)
    while(True):
        #print('step 0')
        datastr = queue.pop(confdata["queuename"])
        #print('step 1')

        if (datastr == None):
            SingleLogger().log.debug("has no data")
            break

        data = parser.tryparse(datastr)
        #入库


#主控程序
#1、读取配置文件
#2、将监控App插入到消息队列
#3、启动线程池
class MainControl(object):
    def __init__(self, confpath='config.json', sleeptime=180, poolsize=10,rule0server=None,rule1server=None):
        self.poolsize = poolsize
        self.pool = threadpool.ThreadPool(poolsize)
        self.confpath = confpath
        self.sleeptime = sleeptime
        global Rule0server
        global Rule1server
        Rule0server = rule0server
        Rule1server = rule1server

    #获取配置文件的数据（需要监控的app参数）
    def getconfdatas(self):
        with open(self.confpath) as f:
            confs = json.load(f)
            return confs


    #启动线程解析
    def startthread(self):
        #queue2 = MyQueue(db=0,host='192.168.10.1')
        while(True):
            confdatas = self.getconfdatas()
            # print("confdatas is:", confdatas)
            # tmp_conf = {"server0":self.rule0server,"server1":self.rule1server,"conf":confdatas}
            requests = threadpool.makeRequests(flowparse, confdatas)
            for req in requests:
                self.pool.putRequest(req)

            sleep(self.sleeptime)













