#-*- coding: UTF-8 -*-
from analysis.rule import Rule
from util import *
import pymysql
from mysqldb.mysql_helper import MySQLHelper

class ColumnRule(Rule):
    def execute(self,res_msg,extra=None):
        super().execute(res_msg,extra)

    @staticmethod
    def add_resource_to_queue(res_msg):
        # 插入消息队列
        SingleLogger().log.debug('kk')

# 自媒体号识别规则
class WeMediaRule(Rule):
    def execute(self,res_msg,extra=None):
        super().execute(res_msg,extra)
    # level0的规则重写
    def _level0_execute(self,res_id,resource,table,extra=None):
        conn = MySQLHelper.pool_connection.get_connection()
        # 创建游标
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

        row_count = cursor.execute("""select * 
                                      from analysis_we_media 
                                      where we = '%s'""" % (resource["source"]))
        if row_count ==0 :
            table.insert({"res_id": res_id})
            pass

        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def add_resource_to_queue(res_msg):
        # 插入消息队列
        SingleLogger().log.debug('kk')

class KeyWordRule(Rule):
    def execute(self,res_msg,extra=None):
        super().execute(res_msg,extra)

    @staticmethod
    def add_resource_to_queue(res_msg):
        # 插入消息队列
        SingleLogger().log.debug('kk')