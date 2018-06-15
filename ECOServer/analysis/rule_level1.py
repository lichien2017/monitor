from threading import Thread
from concurrent import futures
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
        # 规则级别，数据源的mongodb表格，资源列名用于0级处理
        Rule.__init__(self,settings["level"],settings["mongodb_tablename"],settings["res_columns"],settings["extra_rule_data"])
        self._settings = settings
        self.interval = 1
        self.thread_stop = False

    def do_rule1(self):
        while True:
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
                    self.execute_other(res_msg["res_id"], resource, res_msg["time"], res_msg["record_time"],self._extra_data)  # 扩展数据里面可能是阈值
            else:
                time.sleep(1)
        pass
    def do_recv(self):
        while True:
            item = RedisHelper.strict_redis.rpop("recvjob:%s" % (self.__class__.__name__))
            if item != None:
                SingleLogger().log.debug(item)
                # print(self._mongodb_tablename)
                res_recv = item.decode("utf-8").split(",")  # res_id,time,record_time|res_id,time,video,record_time
                sub_job = "sendjob:%s:%s" % (self.__class__.__name__, res_recv[0])  # 子任务消息key
                SingleLogger().log.info(sub_job)
                hset_keys = RedisHelper.strict_redis.hkeys(sub_job)  # 得到任务所有keys，用于检查是否完成校验，等到服务返回
                remove_flag = 1  # 是否删除标示
                inserted = 0  # 可以插入数据库
                for key in hset_keys:
                    rel = RedisHelper.strict_redis.hget(sub_job, key)
                    if rel == None :
                        continue
                    key_value = rel.decode("utf-8") # 检查结果值 -1 表示未处理，0 表示没有问题 1和不为空表示有问题
                    video_json = {} # 用于保存视频图片结果数据
                    if key_value.isdigit() or key_value == "-1": # 如果是数字，可能的值是-1,0,1
                        rel = int(key_value) # 直接转成数值
                    else:
                        rel = 1 # 非数字表示视频的处理，所以这里肯定是因为有问题，那么直接赋值为1
                        video_json = json.loads(key_value) # 将传过来的json字符串进行反序列化
                        pass


                    #rel = int(rel.decode("utf-8")) # 得到结果，1表示有问题，0 表示没有问题
                    # SingleLogger().log.debug("ret = %d" % rel)
                    if rel == 1 and inserted == 0:
                        # 只要有一个为1，表示规则匹配成功，插入数据库
                        SingleLogger().log.info(self._mongodb_tablename + res_recv[1])
                        self._mongodb = self._mongodb_client['crawlnews']
                        table = self._mongodb[self._mongodb_tablename + res_recv[1]]
                        item = table.find_one({"res_id": "%s" % res_recv[0]})
                        if item == None:
                            # 插入到指定有问题的数据表中，比如血腥暴力、色情表
                            table.insert({"res_id": "%s" % res_recv[0],"record_time":res_recv[3]})

                            # 同时将有问题的数据加入到每天的合计表中
                            total_table = self._mongodb["all_resource" + res_recv[1]]
                            total_item = total_table.find_one({"res_id": "%s" % res_recv[0]})
                            if total_item == None :# 如果不存在就插入
                                tmp_res = self._get_resource("%s" % res_recv[0], res_recv[1])
                                if not key.isdigit() :
                                    # lzq 20180608 增加对视频的处理
                                    tmp_content = ""
                                    if key.decode("utf-8").startswith("video"):
                                        tmp_content = tmp_res["video"]
                                    else:
                                        tmp_content = tmp_res[key.decode("utf-8")]
                                    total_table.insert({"res_id": "%s" % res_recv[0],"badkey":"%s" % key.decode("utf-8"),"badcontent":tmp_content,"app_tag":tmp_res["app_tag"],"category_tag":tmp_res["category_tag"]})
                                else:
                                    logo = tmp_res["logo"].split(",")
                                    images = tmp_res["gallary"].split(",")
                                    logo = [x for x in logo if
                                            x != '' and (x.startswith("http://") or x.startswith("https://"))]
                                    images = [x for x in images if
                                              x != '' and (x.startswith("http://") or x.startswith("https://"))]
                                    gallary = logo + images
                                    key_index = int(key.decode("utf-8")) - 1
                                    if key_index <0 or key_index >= len(gallary) :
                                        SingleLogger().log.debug("key_index = %d and gallary len is %d" %(key_index,len(gallary)))
                                    else:
                                        total_table.insert(
                                        {"res_id": "%s" % res_recv[0], "badkey":"%s" % key.decode("utf-8"), "badcontent": gallary[key_index],"app_tag":tmp_res["app_tag"],"category_tag":tmp_res["category_tag"]})

                        # 同时对于视频的结果要存入到视频记录表中 lzq add
                        if key.decode("utf-8").startswith("video"):  # key是video开头表示视频
                            self._mongodb = self._mongodb_client['crawlnews']
                            video_table = self._mongodb["VideoPictures" + res_recv[1]]
                            video_item = video_table.find_one({"res_id": "%s" % res_recv[0]})
                            if video_item == None:
                                video_table.insert({"res_id": "%s" % res_recv[0], "save_path": video_json["save_path"],
                                                    "images": video_json["images"]})
                            pass
                        inserted = 1
                    if rel == -1:
                        remove_flag = 0

                if remove_flag == 1:
                    RedisHelper.strict_redis.delete(sub_job)
            else:
                time.sleep(1)
        pass

    def run(self):
        future_list = []
        try:
            with futures.ThreadPoolExecutor(max_workers=20) as executor:
                future = executor.submit(self.do_rule1)
                future_list.append(future)
                future = executor.submit(self.do_recv)
                future_list.append(future)
                futures.wait(future_list)
                i = 1
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

# 宗教
class ZongJiaoRule(BaseLevel1Rule):
    def __init__(self, settings):
        BaseLevel1Rule.__init__(self, settings)

# 标题党
class BiaoTiDangRule(BaseLevel1Rule):
    def __init__(self, settings):
        BaseLevel1Rule.__init__(self, settings)

# ORC匹配
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