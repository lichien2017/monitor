#-*- coding: UTF-8 -*-
from analysis.rule import Rule

class ColumnRule(Rule):
    def execute(self,resource_id,extra=None):
        super().execute(resource_id,extra)

    @staticmethod
    def add_resource_to_queue(resource_id):
        # 插入消息队列
        print('kk')

class KeyWordRule(Rule):
    def execute(self,resource_id,extra=None):
        super().execute(resource_id,extra)

    @staticmethod
    def add_resource_to_queue(resource_id):
        # 插入消息队列
        print('kk')