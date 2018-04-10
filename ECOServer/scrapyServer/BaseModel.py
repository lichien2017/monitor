# coding=utf-8
import redis
import json
import threadpool
import sys
from time import sleep
from pymongo import MongoClient
from config import ConfigHelper


#消息队列
class MyQueue(object):
    def __init__(self,db=7, host='localhost'):
        self.rcon = redis.Redis(host=host, port=6379, db=db)
        #print("db is:",db)
        # self.queue = queuename

    def pop(self, queuename):
        obj = self.rcon.rpop(queuename)
        return obj

    def push(self, queuename, obj):
        self.rcon.lpush(queuename, obj)

#解析基类
class BaseParse(object):
    def __init__(self,name):
        self.name = name
        print(name)

    #插入mongodb
    def db(self,sdata,articleid,title):
        conn = MongoClient(ConfigHelper.mongodbip, 27017)
        db = conn.crawlnews  #连接crawlnews数据库
        my_originnews = db.originnews
        #查询是否存在此唯一标识的数据
        artcount= my_originnews.find({"identity": str(articleid)}).count()
        if artcount>0:
            sdata['identity']=genearteMD5(title+str(articleid))
            #查询是否存在此标题的数据
            titlecount= my_originnews.find({"title": str(title)}).count()
            if titlecount>0:
                return
        #插入数据库
        my_originnews.save(sdata)
        # 把数据分发给打标服务，服务分为两类，一类基础服务（0），一类高级服务（1）
        # Rule0server.execute_all(articleid)
        # Rule1server.add_resource_to_all_queue(articleid)
        queue = MyQueue(db=ConfigHelper.redisdb, host=ConfigHelper.redisip)
        queue.push(ConfigHelper.analysis_msgqueue,articleid)
    #每个App解析方法重载该方法
    def tryparse(self,str):
        None

#生成md5
def genearteMD5(strs):
    # 创建md5对象
    hl = hashlib.md5()
    # Tips
    # 此处必须声明encode
    # 否则报错为：hl.update(str) Unicode-objects must be encoded before hashing
    hl.update(strs.encode("utf-8"))
    return hl.hexdigest()

#解析框架，做为线程池的处理函数流程
#1、创建解析对象
#2、读取对应消息队列，没有则跳出
#3、解析
#4、入库
def flowparse(confdata):
    #create BaseParse by reflact
    #parser = BaseParse(confdata["parsername"])
    # confdata = confobj["conf"]
    print('the confdata is:', confdata)

    amod = __import__(confdata["modname"], fromlist=True)
    #amod = __import__("ToutiaoModel", fromlist=True)
    print('imported modname')
    aclass = getattr(amod, confdata["classname"])
    parser = aclass(confdata["classname"])

    print('created confdata')
    queue = MyQueue(db=ConfigHelper.redisdb,host=ConfigHelper.redisip)
    while(True):
        #print('step 0')
        datastr = queue.pop(confdata["queuename"])
        #print('step 1')

        if (datastr == None):
            print("has no data")
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
        # global Rule0server
        # global Rule1server
        # Rule0server = rule0server
        # Rule1server = rule1server

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













