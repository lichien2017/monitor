from threading import Thread
from pymongo import MongoClient
from bson import ObjectId
from bson.int64 import Int64
import time
import datetime
import redis
import json
from util import *

# log = Logger()

time_format = "%Y-%m-%d %H:%M:%S"
interval = 10 #10分钟间隔
DAYS = 0 # 与今天的差异，0 标示处理当天，-1标示处理前一天


# pool = redis.ConnectionPool(host=ConfigHelper.redisip, port=ConfigHelper.redisport, db=ConfigHelper.redisdb)
# redis_server = redis.StrictRedis(connection_pool=pool)

class ScreenCaptureMatch(Thread):

    def __init__(self):
        # SingleLogger().log.debug("ScreenCaptureMatch")
        Thread.__init__(self)
        self._client = MongoClient(ConfigHelper.mongodbip, ConfigHelper.mongodbport)
        self._database = self._client["crawlnews"]
        self.thread_stop = False
        pass

    def queryPictures(self,query_date,pkg_time,app_tag,category_tag):
        start_time1 = datetime.datetime.strptime(pkg_time,time_format)

        start_time = start_time1 + datetime.timedelta(minutes=-1)
        end_time = start_time1 + datetime.timedelta(minutes=interval)

        SingleLogger().log.debug(start_time)
        SingleLogger().log.debug(end_time)

        query = {}
        query["tag"] = app_tag
        query["reference"] = category_tag

        query["time"] = {
            u"$gte": start_time.strftime(time_format)
        }

        query["$and"] = [
            {
                u"time": {
                    u"$lt": end_time.strftime(time_format)
                }
            }
        ]

        # {'time': {'$gte': '2018-04-19 01:42:57'}, '$and': [{'time': {'$lte': '2018-04-19 02:42:57'}}]}
        # {'time': {'$gte': '2018-04-19 01:42:59'}, '$and': [{'time': {'$lte': '2018-04-19 01:47:59'}}]}
        SingleLogger().log.debug(query)

        # now = LocalTime.now()  # datetime.datetime.now()
        # date = now + datetime.timedelta(days=DAYS)
        # log.debug(date.strftime("%Y%m%d"))
        collection = self._database["runner_logs"+ query_date]
        cursor = collection.find(query)
        try:
            pic = []
            seq = []
            for doc in cursor:
                # print(doc)
                pic.append(doc["screenshot"])
                seq.append(doc["screen"])
        finally:
            pass
        SingleLogger().log.debug(pic)
        return pic,seq

        pass

    def __get_resource(self,resouce_id,date):
        SingleLogger().log.debug("_get_resource:%s" % resouce_id)
        self._database = self._client['crawlnews']
        res = self._database["originnews"+date].find_one({"identity":"%s" % (resouce_id)})
        if res == None :
            return None
        # SingleLogger().log.debug(res)
        return res

    def write_to_queue(self,res_id,title,pics,seqs):
        data =  {"resid":res_id,"title":title,"imgs":pics,"seqs":seqs}
        json_str = json.dumps(data)
        SingleLogger().log.debug(json_str)
        RedisHelper.strict_redis.lpush("ocr:queue",json_str)
        pass

    def update_status(self,collection,_id,status):
        query = {}
        query["_id"] = {
            u"$in": [
                _id
                 # ObjectId("5ad7f428a06c270001f3bd0a"),
                 # ObjectId("5ad7f59ca06c270001683367")
            ]
        }
        update_set = {
                        u"$set" :
                            {
                                "status" : status
                            }
                     }
        #query["_id"]["$in"].append(_id)
        collection.update(query,update_set,False,True)
        pass

    def send_data(self):
        #local_time = LocalTime.now() #datetime.datetime.fromtimestamp(time.time())
        now = LocalTime.now() #datetime.datetime.now()
        date = now + datetime.timedelta(days=DAYS)
        SingleLogger().log.debug(date.strftime("%Y%m%d"))

        collection = self._database["screencapocr" + date.strftime("%Y%m%d")]
        # 查询条件
        query = {}
        query["status"] = Int64(0)
        screencap_cursor = collection.find(query, limit=10)
        try:
            for item in screencap_cursor:
                SingleLogger().log.debug(item)
                res = self.__get_resource(item["res_id"],date.strftime("%Y%m%d"))  # 获取资源详情
                pictures, seqs = self.queryPictures(date.strftime("%Y%m%d"),item["time"],item["app_tag"],item["category_tag"])
                if len(pictures) > 0:
                    SingleLogger().log.debug("找到了图片，长度为:%d",len(pictures))
                    self.write_to_queue(item["res_id"], res["title"], pictures, seqs)
                    SingleLogger().log.debug("update screencap id = %s status=%d", item["_id"],1)
                    self.update_status(collection, item["_id"], 1)
                else:
                    self.update_status(collection, item["_id"], -1)
        finally:
            pass
            # self._client.close()
        return collection
        pass
    # 回写状态
    def recv_data(self,collection):
        data = RedisHelper.strict_redis.rpop("ocr:result")
        if data != None:
            SingleLogger().log.debug(data)
            item_str = data.decode("utf-8")
            item = json.loads(item_str)
            SingleLogger().log.debug(item)
            query = {}
            query["res_id"] = {
                u"$in": [
                    item["resid"]
                    # ObjectId("5ad7f428a06c270001f3bd0a"),
                    # ObjectId("5ad7f59ca06c270001683367")
                ]
            }
            update_set = {
                u"$set":
                    {
                        u"image": item["img"],
                        u"screen_index" : item["seq"],
                        u"status": 2
                    }
            }
            # query["_id"]["$in"].append(_id)
            collection.update(query, update_set, False, True)
        pass

    def run(self):
        while not self.thread_stop:
            collection = self.send_data()
            self.recv_data(collection)
            time.sleep(3)

        pass