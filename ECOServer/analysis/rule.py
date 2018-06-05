#-*- coding: UTF-8 -*-
import pymongo

# from scrapyServer.config import ConfigHelper
import redis
import json
import time
from util import *
# from util.log import Logger
# log = Logger()

class Rule:
    _mongodb_client = None
    _mongodb = None
    _res_columns = None
    _extra_data = None
    _mongodb_tablename = None
    _level = 0

    # __pool = redis.ConnectionPool(host=ConfigHelper.redisip, port=ConfigHelper.redisport, db=ConfigHelper.redisdb)
    # _redis_server = redis.StrictRedis(connection_pool=__pool)

    def __init__(self,level,mongodb_table,res_columns=None,extra_data = None):
        if res_columns != None :
            self._res_columns = res_columns.split('|')
        if extra_data != None :
            self._extra_data = extra_data.split('|')
        if mongodb_table == None:
            self._mongodb_tablename = self.__class__.__name__;
        else:
            self._mongodb_tablename = mongodb_table
        # 每次添加插入到当天的数据表中，所以需要在名字加上当天日期 time.strftime('%Y%m%d',time.localtime(time.time()))
        #self._mongodb_tablename = self._mongodb_tablename + LocalTime.now().strftime('%Y%m%d')
        self._level = level
        self._mongodb_client = pymongo.MongoClient(ConfigHelper.mongodbip, ConfigHelper.mongodbport)
        # 定义与原子服务通讯的消息队列名称
        self.queue_name_text = self.__class__.__name__ + ":text"
        self.queue_name_image = self.__class__.__name__ + ":image"
        self.queue_name_video = self.__class__.__name__ + ":video"

    # 通过资源id和资源抓取的时间找到资源详情
    def _get_resource(self,res_id,date):
        SingleLogger().log.debug("_get_resource:%s" % res_id)
        SingleLogger().log.debug("_mongodb = %s",'crawlnews'+LocalTime.get_local_date(date,"%Y%m%d").strftime("%Y%m"))
        self._mongodb = self._mongodb_client['crawlnews']
        # 从指定日期的分表中查询数据
        SingleLogger().log.debug("table = %s", "originnews"+date)
        res = self._mongodb["originnews"+date].find_one({"identity":"%s" % (res_id)})
        if res == None :
            return None
        SingleLogger().log.debug(res)
        return res
    # 0 level规则处理函数
    def _level0_execute(self,res_id,resource,table,extra=None):
        if self._res_columns == None or self._extra_data == None :
            SingleLogger().log.debug("_level0_execute 函数没有可用的数据执行")
            return
        for col in self._res_columns :
            for keyword in self._extra_data :
                SingleLogger().log.debug("%s列的数据'%s'是否包含关键字'%s'" % (col,resource[col],keyword))
                if resource[col] == keyword or resource[col].find(keyword) >=0:  # 匹配关键字
                    # 关键字匹配上了，插入到对应的数据表格中
                    #table = self._mongodb[self._mongodb_tablename+LocalTime.now_str()]
                    table.insert({"res_id": res_id})
                    return
    # 创建子任务id
    def build_sub_job_id(self,res_id):
        sub_job_id = "sendjob:%s:%s" % (self.__class__.__name__, res_id)  # 子任务消息key
        return sub_job_id

    # 构建消息包
    def build_post_msg(self,sub_job_id,extra):
        threshold = 0.5
        if extra !=None and len(extra)>0 :
            threshold = float(extra[0])

        # 返回消息队列带上日期
        normal_msg = {"id": sub_job_id, "seq": 1, "data": [], "threshold": threshold, "resdata": "",
         "resp": "recvjob:%s" % (self.__class__.__name__)}

        return normal_msg
    # 非0 level规则处理函数
    def execute_other(self,res_id,resource,crawl_time_str,extra=None):
        SingleLogger().log.debug('其他处理方式') # 但是这里不需要实现，由各实现类的线程函数直接处理了，如果实现了，那实质上是同步调用方式
        if resource == None :
            return
        # title = resource["title"]
        # description = resource["description"]
        # content = resource["content"]
        logo = resource["logo"].split(",")
        images = resource["gallary"].split(",")
        sub_job = self.build_sub_job_id(res_id) #"sendjob:%s:%s" % (self.__class__.__name__,res_id) #子任务消息key

        normal_msg = self.build_post_msg(sub_job,extra) #{"id":sub_job,"seq":"","data":[],"threshold":threshold,"resdata":"","resp":"recvjob:%s" %(self.__class__.__name__)}

        # 处理文字字段，需要匹配的
        if self._res_columns !=None and len(self._res_columns)>0 :
            for col in self._res_columns :
                RedisHelper.strict_redis.hset(sub_job, col, -1)
                normal_msg["seq"] = col
                normal_msg["data"] = [resource[col]]
                normal_msg["resdata"] = "%s,%s" % (res_id,crawl_time_str)
                SingleLogger().log.debug("title package:%s", normal_msg)
                # 将数据插入到指定的处理消息队列
                RedisHelper.strict_redis.lpush(self.queue_name_text, json.dumps(normal_msg))


        index = 1

        # 创建image
        # 图片保存路径 相对路径，日期/资源id/文件名
        media_savepath = "%s/%s/%s" % (ConfigHelper.analysis_savepath,crawl_time_str,res_id)
        # self._check_dir(media_savepath)

        logo = [x for x in logo if x != '' and (x.startswith("http://") or x.startswith("https://"))]

        for x in logo :
            RedisHelper.strict_redis.hset(sub_job, index, -1)
            normal_msg["seq"] = index
            normal_msg["data"] = [x,"%s/%s/%s"%(ConfigHelper.download_savepath,crawl_time_str,Secret.md5(x)),"%s/%s" % (media_savepath,Secret.md5(x))]
            normal_msg["resdata"] = "%s,%s" % (res_id,crawl_time_str)
            RedisHelper.strict_redis.lpush(self.queue_name_image, json.dumps(normal_msg))
            index += 1

        images = [x for x in images if x != '' and (x.startswith("http://") or x.startswith("https://"))]
        for x in images :
            RedisHelper.strict_redis.hset(sub_job, index, -1)
            normal_msg["seq"] = index
            normal_msg["data"] = [x, "%s/%s/%s" % (ConfigHelper.download_savepath,crawl_time_str, Secret.md5(x)),
                                  "%s/%s" % (media_savepath, Secret.md5(x))]
            normal_msg["resdata"] = "%s,%s" % (res_id,crawl_time_str)
            RedisHelper.strict_redis.lpush(self.queue_name_image, json.dumps(normal_msg))
            index += 1


    # 规则处理总入口，根据level进行分发
    # res_msg {res_id:xxxx,time:xxxx}
    def execute(self,res_msg_json,extra=None):
        item = json.loads(res_msg_json) # 转换成dict
        SingleLogger().log.debug("规则:%s,正在处理:resource_id=%s" % (self.__class__.__name__,item["res_id"]))
        resource = self._get_resource(item["res_id"],item["time"])
        if resource != None:
            # SingleLogger().log.debug("资源找到了，检查结果表中是否存在数据:%s%s" %(self._mongodb_tablename,resource["time"]))
            table = self._mongodb[self._mongodb_tablename+item["time"]]
            # SingleLogger().log.debug(table)
            try:
                rows = table.find({"res_id": item["res_id"]})
                if rows.count() == 0:  # 如果不存在数据表中，则开始判断是否能匹配上规则
                    if self._level == 0 :
                        self._level0_execute(item["res_id"],resource,table,extra)
                    else:
                        self.execute_other(item["res_id"],resource,item["time"],extra)
            except Exception as e:
                SingleLogger().log.error(e)
                pass

        return 0




    @staticmethod
    def add_resource_to_queue(res_msg,name):
        # 插入消息队列
        print('Rule add_resource_to_queue :'+res_msg)

class RuleFactory:
    @staticmethod
    def get_class(settings):
        SingleLogger().log.debug("module:"+settings["imp_python_module"])
        ip_module = __import__(settings["imp_python_module"])
        # dir()查看模块属性
        SingleLogger().log.debug(dir(ip_module))
        # 使用getattr()获取imp_module的类
        obj_class = getattr(ip_module, settings["imp_python_class"])
        return obj_class
    # 动态创建一个规则实例
    @staticmethod
    def create_instance(settings):
        # 使用getattr()获取imp_module的类
        obj_class = RuleFactory.get_class(settings)
        # 动态加载类runner_class生成类对象
        instance = obj_class(settings["level"],settings["mongodb_tablename"],settings["res_columns"],settings["extra_rule_data"])  # 实例化一个runner
        return instance


