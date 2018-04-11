from threading import Thread

import redis

from analysis.rule import Rule
from scrapyServer.config import ConfigHelper

pool = redis.ConnectionPool(host=ConfigHelper.redisip, port=6379, db=ConfigHelper.redisdb)
redis_server = redis.StrictRedis(connection_pool=pool)
class XueXingBaoLiRule(Rule,Thread):

    def __init__(self,settings):
        Thread.__init__(self)
        Rule.__init__(self,settings["level"],settings["mongodb_tablename"])
        self._settings = settings
        self.interval = 1
        self.thread_stop = False

    def run(self):
        while not self.thread_stop:
            item = self._redis_server.brpop(self.__name__ + ":queue")
            print(item)
            res_id = item[1].decode("utf-8")
            print("%s 获取到数据:%s" % (self.__name__,res_id))
            resource = self._get_resource(res_id)
            if resource !=None :
                print("%s 获取到数据:%s" % (self.__name__,resource))
                self.execute_other(res_id,resource)


    @staticmethod
    def add_resource_to_queue(resource_id,class_name):
        # 插入消息队列
        print('XueXingBaoLiRule add_resource_to_queue :' + resource_id)
        redis_server.lpush(class_name + ":queue",resource_id)

