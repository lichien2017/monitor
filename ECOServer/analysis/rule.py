#-*- coding: UTF-8 -*-
import pymongo

from ruleServer.config import ConfigHelper


class Rule:
    _mongodb_client = None
    _mongodb = None
    _res_columns = None
    _extra_data = None
    _mongodb_tablename = None
    _level = 0
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

    def _get_resource(self,resouce_id):
        self._mongodb = self._mongodb_client['crawlnews']
        rows = self._mongodb.originnews.find({"identity":resouce_id})
        if rows == None or rows.count() == 0:
            return None
        # print(rows)
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
        print('其他处理方式')

    def execute(self,resource_id,extra=None):
        print("规则:%s,正在处理:resource_id=%s" % (self.__class__.__name__,resource_id))
        resource = self._get_resource(resource_id)
        if resource != None:
            table = self._mongodb[self._mongodb_tablename]
            rows = table.find({"res_id": resource_id})
            if rows.count() == 0:  # 如果不存在数据表中，则开始判断是否能匹配上规则
                if self._level == 0 :
                    self._level0_execute(resource_id,resource,extra)
                else:
                    self.execute_other(resource_id,resource,extra)
        return 0

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


