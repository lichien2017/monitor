from threading import Thread
from pymongo import MongoClient
from bson import ObjectId
from bson.int64 import Int64
import time
import datetime
import redis
import json

from util.tymx_time import LocalTime
from scrapyServer.config import ConfigHelper
from util.log import Logger

log = Logger()

time_format = "%Y-%m-%d %H:%M:%S"
interval = 10 #10分钟间隔

pool = redis.ConnectionPool(host=ConfigHelper.redisip, port=6379, db=ConfigHelper.redisdb)
redis_server = redis.StrictRedis(connection_pool=pool)

class ScreenCaptureMatch(Thread):

    def __init__(self):
        Thread.__init__(self)
        self._client = MongoClient(ConfigHelper.mongodbip, 27017)
        self._database = self._client["crawlnews"]
        self.thread_stop = False
        pass

    def queryPictures(self,pkg_time):
        start_time = datetime.datetime.strptime(pkg_time,time_format)
        end_time = start_time + datetime.timedelta(minutes=interval)

        log.debug(start_time)
        log.debug(end_time)
        query = {}
        query["time"] = {
            u"$gte": start_time.strftime(time_format)
        }

        query["$and"] = [
            {
                u"time": {
                    u"$lte": end_time.strftime(time_format)
                }
            }
        ]

        # {'time': {'$gte': '2018-04-19 01:42:57'}, '$and': [{'time': {'$lte': '2018-04-19 02:42:57'}}]}
        # {'time': {'$gte': '2018-04-19 01:42:59'}, '$and': [{'time': {'$lte': '2018-04-19 01:47:59'}}]}
        log.debug(query)

        now = LocalTime.now()  # datetime.datetime.now()
        date = now + datetime.timedelta(days=-1)
        log.debug(date.strftime("%Y%m%d"))
        collection = self._database["runner_logs"+ date.strftime("%Y%m%d")]
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
        log.debug(pic)
        return pic,seq

        pass

    def __get_resource(self,resouce_id):
        log.debug("_get_resource:%s" % resouce_id)
        self._database = self._client['crawlnews']
        res = self._database.originnews.find_one({"identity":"%s" % (resouce_id)})
        if res == None :
            return None
        log.debug(res)
        return res

    def write_to_queue(self,res_id,title,pics,seqs):
        data =  {"resid":res_id,"title":title,"imgs":pics,"seqs":seqs}
        json_str = json.dumps(data)
        log.debug(json_str)
        redis_server.lpush("ocr:queue",json_str)
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
        date = now + datetime.timedelta(days=-1)
        log.debug(date.strftime("%Y%m%d"))

        collection = self._database["screencapocr" + date.strftime("%Y%m%d")]
        # 查询条件
        query = {}
        query["status"] = Int64(0)
        screencap_cursor = collection.find(query, limit=10)
        try:
            for item in screencap_cursor:
                log.debug(item)
                res = self.__get_resource(item["res_id"])  # 获取资源详情
                pictures, seqs = self.queryPictures(item["time"])
                if len(pictures) > 0:
                    self.write_to_queue(item["res_id"], res["title"], pictures, seqs)
                    self.update_status(collection, item["_id"], 1)
        finally:
            pass
            # self._client.close()
        return collection
        pass

    def recv_data(self,collection):
        data = redis_server.rpop("ocr:result")
        if data != None:
            log.debug(data)
            item_str = data.decode("utf-8")
            item = json.loads(item_str)
            log.debug(item)
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
                        u"seq" : item["seq"]
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