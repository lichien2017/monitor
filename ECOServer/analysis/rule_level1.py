from threading import Thread

import redis
import time
from analysis.rule import Rule
from scrapyServer.config import ConfigHelper

pool = redis.ConnectionPool(host=ConfigHelper.redisip, port=6379, db=ConfigHelper.redisdb)
redis_server = redis.StrictRedis(connection_pool=pool)

# level1的基础类
class BaseLevel1Rule(Rule,Thread):

    def __init__(self,settings):
        Thread.__init__(self)
        Rule.__init__(self,settings["level"],settings["mongodb_tablename"],settings["res_columns"],settings["extra_rule_data"])
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
                #print(self._mongodb_tablename)
                res_id = item.decode("utf-8")
                sub_job = "sendjob:%s:%s" % (self.__class__.__name__,res_id) #子任务消息key
                hset_keys = self._redis_server.hkeys(sub_job)
                remove_flag = 1 # 是否删除标示
                inserted = 0 # 可以插入数据库
                for key in hset_keys :
                    rel = self._redis_server.hget(sub_job,key)
                    rel = int(rel.decode("utf-8"))
                    print ("ret = %d" % rel)
                    if rel == 1 and inserted == 0:
                        # 只要有一个为1，表示规则匹配成功，插入数据库
                        table = self._mongodb[self._mongodb_tablename]
                        item = table.find_one({"res_id": res_id})
                        if item == None :
                            table.insert({"res_id": res_id})
                        inserted = 1
                    if rel == -1 :
                        remove_flag = 0

                if remove_flag == 1:
                    self._redis_server.delete(sub_job)

            time.sleep(1)


    @staticmethod
    def add_resource_to_queue(resource_id,class_name):
        # 插入消息队列
        print("add_resource_to_queue :%s" % (resource_id))
        redis_server.lpush(class_name + ":queue",resource_id)

#血腥暴力
class XueXingBaoLiRule(BaseLevel1Rule):
     def __init__(self,settings):
        BaseLevel1Rule.__init__(self,settings)

#色情
class SexyRule(BaseLevel1Rule):
    def __init__(self, settings):
        BaseLevel1Rule.__init__(self, settings)
#政治有害
class PoliticalRule(BaseLevel1Rule):
    def __init__(self, settings):
        BaseLevel1Rule.__init__(self, settings)

# 政治有害
class ZongJiaoRule(BaseLevel1Rule):
    def __init__(self, settings):
        BaseLevel1Rule.__init__(self, settings)

# 政治有害
class BiaoTiDangRule(BaseLevel1Rule):
    def __init__(self, settings):
        BaseLevel1Rule.__init__(self, settings)