#-*- coding: UTF-8 -*-  
'''
@描述：日志输入封装
'''

import logging.handlers
import os
import sys

class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance

class Logger(logging.Logger):
    def __init__(self, filename=None):
        super(Logger, self).__init__(self)

        # 日志文件名
        if filename is None:
            filename = '/mnt/db/logs/pt.log'

        if not os.path.exists("/mnt/db/logs") :
            os.makedirs("/mnt/db/logs")
        self.filename = filename

        # 创建一个handler，用于写入日志文件 (每天生成1个，保留30天的日志)
        fh = logging.handlers.TimedRotatingFileHandler(self.filename, 'D', 1, 30)
        fh.suffix = "%Y%m%d-%H%M.log"
        fh.setLevel(logging.DEBUG) 

        # 再创建一个handler，用于输出到控制台 
        ch = logging.StreamHandler() 
        ch.setLevel(logging.DEBUG) 

        # 定义handler的输出格式 
        formatter = logging.Formatter('[%(asctime)s] - %(filename)s [Line:%(lineno)d] - [%(levelname)s]-[thread:%(thread)s]-[process:%(process)s] - %(message)s') 
        fh.setFormatter(formatter) 
        ch.setFormatter(formatter) 

        # 给logger添加handler 
        self.addHandler(fh)
        self.addHandler(ch) 

class SingleLogger(Singleton):
    def __init__(self):
        path = sys.argv[0].split("/")
        self.log = Logger(path[-1].split(".")[0])
        pass
if __name__ == '__main__':
    pass