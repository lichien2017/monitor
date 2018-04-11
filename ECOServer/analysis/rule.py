#-*- coding: UTF-8 -*-
import pymongo

from scrapyServer.config import ConfigHelper
import redis
import hashlib
import os

class Rule:
    _mongodb_client = None
    _mongodb = None
    _res_columns = None
    _extra_data = None
    _mongodb_tablename = None
    _level = 0

    __pool = redis.ConnectionPool(host=ConfigHelper.redisip, port=6379, db=ConfigHelper.redisdb)
    _redis_server = redis.StrictRedis(connection_pool=__pool)

    def __init__(self,level,mongodb_table,res_columns=None,extra_data = None):
        if res_columns != None :
            self._res_columns = res_columns.split('|')
        if extra_data != None :
            self._extra_data = extra_data.split('|')
        if mongodb_table == None:
            self._mongodb_tablename = self.__class__.__name__;
        else:
            self._mongodb_tablename = mongodb_table
        self._level = level
        self._mongodb_client = pymongo.MongoClient(ConfigHelper.mongodbip, 27017)
        # 定义与原子服务通讯的消息队列名称
        self.queue_name_text = self.__class__.__name__ + ":text"
        self.queue_name_image = self.__class__.__name__ + ":image"
        self.queue_name_video = self.__class__.__name__ + ":video"

    def _get_resource(self,resouce_id):
        print("_get_resource:%s" % resouce_id)
        self._mongodb = self._mongodb_client['crawlnews']
        rows = self._mongodb.originnews.find({"identity":"%s" % (resouce_id)})
        if rows == None or rows.count() == 0:
            return None
        print(rows)
        return rows[0]

    def _level0_execute(self,res_id,resource,extra=None):
        if self._res_columns == None or self._extra_data == None :
            print("_level0_execute 函数没有可用的数据执行")
            return
        for col in self._res_columns :
            for keyword in self._extra_data :
                print("%s列的数据'%s'是否包含关键字'%s'" % (col,resource[col],keyword))
                if resource[col] == keyword or resource[col].find(keyword) >=0:  # 匹配关键字
                    # 关键字匹配上了，插入到对应的数据表格中
                    table = self._mongodb[self._mongodb_tablename]
                    table.insert({"res_id": res_id})
                    return

    def execute_other(self,res_id,resource,extra=None):
        print('其他处理方式') # 但是这里不需要实现，由各实现类的线程函数直接处理了，如果实现了，那实质上是同步调用方式
        if resource == None :
            return
        title = resource["title"]
        description = resource["description"]
        content = resource["content"]
        logo = resource["logo"].split(",")
        images = resource["gallary"].split(",")
        sub_job = "sendjob:%s:%s" % (self.__class__.__name__,res_id) #子任务消息key
        normal_msg = {"id":sub_job,"seq":"","data":[],"resdata":"","resp":"%s:%s"%(self.__class__.__name__,res_id)}
        # title标签
        self._redis_server.hset(sub_job,"title",-1)
        normal_msg["seq"] = "title"
        normal_msg["data"] = [title]
        normal_msg["resdata"] = "%s,title" % (res_id)
        print("title package:",normal_msg)
        self._redis_server.lpush(self.queue_name_text,normal_msg)
        # description标签
        self._redis_server.hset(sub_job, "description", -1)
        normal_msg["seq"] = "description"
        normal_msg["data"] = [description]
        normal_msg["resdata"] = "%s,description" % (res_id)
        print("description package:", normal_msg)
        self._redis_server.lpush(self.queue_name_text, normal_msg)
        # content标签
        self._redis_server.hset(sub_job, "content", -1)
        normal_msg["seq"] = "content"
        normal_msg["data"] = [content]
        normal_msg["resdata"] = "%s,content" % (res_id)
        print("content package:", normal_msg)
        self._redis_server.lpush(self.queue_name_text, normal_msg)
        index = 1

        # 创建image
        # 图片保存路径
        media_savepath = "%s/%s" % (ConfigHelper.analysis_savepath,res_id)
        self._check_dir(media_savepath)
        for x in logo :
            self._redis_server.hset(sub_job, index, -1)
            normal_msg["seq"] = index
            normal_msg["data"] = [x,"%s/%s"%(ConfigHelper.download_savepath,self.get_md5(x)),"%s/%s" % (media_savepath,self.get_md5(x))]
            normal_msg["resdata"] = "%s,%d" % (res_id,index)
            index=index +1
            self._redis_server.lpush(self.queue_name_image, normal_msg)

        for x in images :
            self._redis_server.hset(sub_job, index, -1)
            normal_msg["seq"] = index
            normal_msg["data"] = [x, "%s/%s" % (ConfigHelper.download_savepath, self.get_md5(x)),
                                  "%s/%s" % (media_savepath, self.get_md5(x))]
            normal_msg["resdata"] = "%s,%d" % (res_id, index)
            index=index +1
            self._redis_server.lpush(self.queue_name_image, normal_msg)

    def execute(self,resource_id,extra=None):
        print("规则:%s,正在处理:resource_id=%s" % (self.__class__.__name__,resource_id))
        resource = self._get_resource(resource_id)
        if resource != None:
            print("资源找到了，检查结果表中是否存在数据")
            table = self._mongodb[self._mongodb_tablename]
            print(table)
            rows = table.find({"res_id": resource_id})
            if rows.count() == 0:  # 如果不存在数据表中，则开始判断是否能匹配上规则
                if self._level == 0 :
                    self._level0_execute(resource_id,resource,extra)
                else:
                    self.execute_other(resource_id,resource,extra)
        return 0


    def _check_dir(self,dir):
        if not os.path.exists(dir):
            os.makedirs(dir)

    def get_md5(self,src):
        m = hashlib.md5()
        m.update(src.encode("utf-8"))
        # print(m.hexdigest())
        return m.hexdigest()

    @staticmethod
    def add_resource_to_queue(resource_id):
        # 插入消息队列
        print('Rule add_resource_to_queue :'+resource_id)

class RuleFactory:
    @staticmethod
    def get_class(settings):
        print("module:"+settings["imp_python_module"])
        ip_module = __import__(settings["imp_python_module"])
        # dir()查看模块属性
        print(dir(ip_module))
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

