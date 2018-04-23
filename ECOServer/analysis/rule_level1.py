from threading import Thread

import redis
import time
import datetime
import json
from analysis.rule import Rule
# from scrapyServer.config import ConfigHelper
from util import *

# log = Logger()


# level1的基础类
class BaseLevel1Rule(Rule,Thread):

    def __init__(self,settings):
        Thread.__init__(self)
        Rule.__init__(self,settings["level"],settings["mongodb_tablename"],settings["res_columns"],settings["extra_rule_data"])
        self._settings = settings
        self.interval = 1
        self.thread_stop = False

    def do_rule1(self):
        # 不同规则从缓存中获取资源id进行处理
        item = RedisHelper.strict_redis.rpop(self.__class__.__name__ + ":queue")
        if item != None:
            SingleLogger().log.debug(item)  # msg = {"res_id":resource_id,"time":LocalTime.now_str()}
            # res_id = item.decode("utf-8")
            res_msg = json.loads(item)
            SingleLogger().log.debug("%s 获取到数据:%s" % (self.__class__.__name__, res_msg["res_id"]))
            resource = self._get_resource(res_msg["res_id"], res_msg["time"])
            if resource != None:
                SingleLogger().log.debug("%s 获取到数据:%s" % (self.__class__.__name__, resource))
                self.execute_other(res_msg["res_id"], resource, res_msg["time"], self._extra_data)  # 扩展数据里面可能是阈值
        pass
    def do_recv(self):
        item = RedisHelper.strict_redis.rpop("recvjob:%s" % (self.__class__.__name__))
        if item != None:
            SingleLogger().log.debug(item)
            # print(self._mongodb_tablename)
            res_recv = item.decode("utf-8").split(",")  # res_id,time
            sub_job = "sendjob:%s:%s" % (self.__class__.__name__, res_recv[0])  # 子任务消息key
            SingleLogger().log.info(sub_job)
            hset_keys = RedisHelper.strict_redis.hkeys(sub_job)
            remove_flag = 1  # 是否删除标示
            inserted = 0  # 可以插入数据库
            for key in hset_keys:
                rel = RedisHelper.strict_redis.hget(sub_job, key)
                rel = int(rel.decode("utf-8"))
                # SingleLogger().log.debug("ret = %d" % rel)
                if rel == 1 and inserted == 0:
                    # 只要有一个为1，表示规则匹配成功，插入数据库
                    SingleLogger().log.info(self._mongodb_tablename + res_recv[1])
                    table = self._mongodb[self._mongodb_tablename + res_recv[1]]
                    item = table.find_one({"res_id": "%s" % res_recv[0]})
                    if item == None:
                        table.insert({"res_id": "%s" % res_recv[0]})
                    inserted = 1
                if rel == -1:
                    remove_flag = 0

            if remove_flag == 1:
                RedisHelper.strict_redis.delete(sub_job)
        pass

    def run(self):
        while not self.thread_stop:
            try:
                # 不同规则从缓存中获取资源id进行处理
                self.do_rule1()
                self.do_recv()
                time.sleep(1)
            except Exception as e:
                SingleLogger().log.error(e)



    @staticmethod
    def add_resource_to_queue(res_msg,class_name):
        # 插入消息队列，从抓包传过来的的资源id，插入到规则处理表
        RedisHelper.strict_redis.lpush(class_name + ":queue",res_msg)

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

# 政治有害
class ScreenCapORCRule(BaseLevel1Rule):
    def __init__(self, settings):
        BaseLevel1Rule.__init__(self, settings)

    def run(self):
        while not self.thread_stop:
            item = RedisHelper.strict_redis.rpop(self.__class__.__name__ + ":queue")
            if item != None :
                SingleLogger().log.debug(item)
                # res_id = item.decode("utf-8")
                res_msg = json.loads(item)
                SingleLogger().log.debug("%s 获取到数据:%s" % (self.__class__.__name__,res_msg["res_id"]))
                resource = self._get_resource(res_msg["res_id"],res_msg["time"])
                if resource !=None :
                    SingleLogger().log.debug("%s 获取到数据:%s" % (self.__class__.__name__,resource))
                    table = self._mongodb[self._mongodb_tablename+res_msg["time"]] #得到数据表对象
                    item = table.find_one({"res_id": "%s" % res_msg["res_id"]}) #是否
                    if item == None:
                        # 每天的数据表格中只保证有一条记录就行了，插入的数据格式
                        # 包括 res_id,time,status,image
                        # local_time = LocalTime.now() #datetime.datetime.fromtimestamp(time.time())
                        # SingleLogger().log.debug(local_time.strftime("%Y-%m-%d %H:%M:%S"))
                        # time_str = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                        table.insert({"res_id": "%s" % res_msg["res_id"],
                                      "time":resource["crawltimestr"],
                                      "app_tag": resource["app_tag"],
                                      "category_tag": resource["category_tag"],
                                      "status":0,"image":"","screen_index":-1})
            time.sleep(1)