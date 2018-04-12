from threading import Thread

import redis
import time
from analysis.rule import Rule
from scrapyServer.config import ConfigHelper

pool = redis.ConnectionPool(host=ConfigHelper.redisip, port=6379, db=ConfigHelper.redisdb)
redis_server = redis.StrictRedis(connection_pool=pool)
class XueXingBaoLiRule(Rule,Thread):

    def __init__(self,settings):
        Thread.__init__(self)
        Rule.__init__(self,settings["level"],settings["mongodb_tablename"],None,settings["extra_rule_data"])
        self._settings = settings
        self.interval = 1
        self.thread_stop = False

    def run(self):
        while not self.thread_stop:
            item = self._redis_server.rpop(self.__class__.__name__ + ":queue")
            if item != None :
                print(item)
                res_id = item.decode("utf-8")
                print("%s 获取到数据:%s" % (self.__class__.__name__,res_id))
                resource = self._get_resource(res_id)
                if resource !=None :
                    print("%s 获取到数据:%s" % (self.__class__.__name__,resource))
                    self.execute_other(res_id,resource,self._extra_data) #扩展数据里面可能是阈值

            item = self._redis_server.rpop("recvjob:%s" % (self.__class__.__name__))
            if item !=None :
                print(item)
                res_id = item.decode("utf-8")
                sub_job = "sendjob:%s:%s" % (self.__class__.__name__,res_id) #子任务消息key
                hset_keys = self._redis_server.hkeys(sub_job)
                for key in hset_keys :
                    rel = self._redis_server.hget(sub_job,key)
                    if rel == 1 :
                        # 只要有一个为1，表示规则匹配成功，插入数据库
                        table = self._mongodb[self._mongodb_tablename]
                        table.insert({"res_id": res_id})
                        break
            time.sleep(1)


    @staticmethod
    def add_resource_to_queue(resource_id,class_name):
        # 插入消息队列
        print("add_resource_to_queue :%s" % (resource_id))
        redis_server.lpush(class_name + ":queue",resource_id)

class SexyRule(Rule,Thread):

    def __init__(self,settings):
        Thread.__init__(self)
        Rule.__init__(self,settings["level"],settings["mongodb_tablename"],None,settings["extra_rule_data"])
        self._settings = settings
        self.interval = 1
        self.thread_stop = False

    def run(self):
        while not self.thread_stop:
            item = self._redis_server.rpop(self.__class__.__name__ + ":queue")
            if item != None :
                print(item)
                res_id = item.decode("utf-8")
                print("%s 获取到数据:%s" % (self.__class__.__name__,res_id))
                resource = self._get_resource(res_id)
                if resource !=None :
                    print("%s 获取到数据:%s" % (self.__class__.__name__,resource))
                    self.execute_other(res_id,resource,self._extra_data) #扩展数据里面可能是阈值

            item = self._redis_server.rpop("recvjob:%s" % (self.__class__.__name__))
            if item !=None :
                print(item)
                res_id = item.decode("utf-8")
                sub_job = "sendjob:%s:%s" % (self.__class__.__name__,res_id) #子任务消息key
                hset_keys = self._redis_server.hkeys(sub_job)
                for key in hset_keys :
                    rel = self._redis_server.hget(sub_job,key)
                    if rel == 1 :
                        # 只要有一个为1，表示规则匹配成功，插入数据库
                        table = self._mongodb[self._mongodb_tablename]
                        table.insert({"res_id": res_id})
                        break
            time.sleep(1)


    @staticmethod
    def add_resource_to_queue(resource_id,class_name):
        # 插入消息队列
        print("add_resource_to_queue :%s" % (resource_id))
        redis_server.lpush(class_name + ":queue",resource_id)