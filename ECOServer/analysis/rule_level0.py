#-*- coding: UTF-8 -*-
from analysis.rule import Rule
from util import *
class ColumnRule(Rule):
    def execute(self,res_msg,extra=None):
        super().execute(res_msg,extra)

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