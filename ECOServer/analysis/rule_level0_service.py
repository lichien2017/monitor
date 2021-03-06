#-*- coding: UTF-8 -*-

"""
处理level0的规则
"""
import threading

import pymysql

from analysis.rule import RuleFactory
from mysqldb.mysql_helper import MySQLHelper

from util import *
# log = Logger()
class RuleServiceLevel0:
    timer = None
    def __init__(self,refresh_rule_time=5):
        self._rule_instance = []
        SingleLogger().log.debug("RuleServiceLevel0")
        self.refresh_rule_time = refresh_rule_time
        timer = threading.Timer(refresh_rule_time,self.load_rules)
        timer.start()

    #加载规则配置
    def load_rules(self,level = 0):
        SingleLogger().log.debug('RuleServiceLevel0 load_rules enter')
        conn = MySQLHelper.pool_connection.get_connection()
        # 创建游标
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        # 执行SQL，并返回收影响行数
        row_count = cursor.execute("select * from analysis_rules where level = %s and isonline = 1", (level))
        self._rule_instance[:] = []
        # 获取所有数据
        result = cursor.fetchone()

        while result != None:
            # print(result)
            rule_instance = RuleFactory.create_instance(result)
            self._rule_instance.append(rule_instance)
            result = cursor.fetchone()
        cursor.close()
        conn.close()
        timer = threading.Timer(self.refresh_rule_time,self.load_rules)
        timer.start()

    # 调用规则方法
    # res_msg = {res_id:xxx,time:xxxx}
    def execute_all(self,res_msg):
        for instance in self._rule_instance:
            instance.execute(res_msg)

class RuleServiceLevel1:
    def __init__(self,load_rule_time):
        self._rule_class = []
        self._settings = []
        self.load_rule_time = load_rule_time
        SingleLogger().log.debug("RuleServiceLevel1")
        timer = threading.Timer(self.load_rule_time,self.load_rules)
        timer.start()
    #加载规则配置
    def load_rules(self,level = 1):
        SingleLogger().log.debug('RuleServiceLevel1 load_rules enter')
        conn = MySQLHelper.pool_connection.get_connection()
        # 创建游标
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        # 执行SQL，并返回收影响行数
        row_count = cursor.execute("select * from analysis_rules where level = %s and isonline = 1", (level))
        self._rule_class[:] = []
        # 获取所有数据
        result = cursor.fetchone()

        while result != None:
            # print(result)
            rule_class = RuleFactory.get_class(result)
            self._rule_class.append(rule_class)
            self._settings.append(result)
            result = cursor.fetchone()
        cursor.close()
        conn.close()
        timer = threading.Timer(self.load_rule_time, self.load_rules)
        timer.start()

    # 启动服务
    def execute_all(self):
        for i in range(0,len(self._rule_class)) :
            instance = self._rule_class[i](self._settings[i])
            instance.start()

    # 将消息发送给相关的规则处理服务
    def add_resource_to_all_queue(self,res_msg):
        for class_name in self._rule_class:
            class_name.add_resource_to_queue(res_msg,class_name.__name__) #动态调用类的静态方法
            # getattr(class_name, "add_resource_to_queue")(resource_id)

if __name__ == "__main__":
    SingleLogger().log.debug('RuleServiceLevel1')
    rule_service_level = RuleServiceLevel1()
    rule_service_level.load_rules()
    rule_service_level.execute_all()

    SingleLogger().log.debug('RuleServiceLevel1')