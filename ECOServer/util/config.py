#-*- coding: UTF-8 -*-
import configparser
import os

debug = 0 # 1表示调试环境

class ConfigHelper:
    # mysqldb.logger.setLevel('DEBUG')
    __config = configparser.ConfigParser()
    localDir = os.path.dirname(__file__)
    if debug == 1:
        __config.read(localDir+"/config_local.ini")
    else:
        __config.read(localDir + "/config.ini")
    mysql_ip = __config.get("mysql", "mysql_ip")
    mysql_user = __config.get("mysql", "mysql_user")
    mysql_pwd = __config.get("mysql", "mysql_pwd")
    mysql_db = __config.get("mysql", "mysql_db")
    mongodbip = __config.get("mongodb", "mongodbip")
    mongodbport = __config.getint("mongodb", "mongodbport")
    redisip = __config.get("redis", "redisip")
    redisdb = __config.get("redis", "redisdb")
    redisport = __config.getint("redis", "redisport")
    load_rule_time = __config.getint("global", "load_rule_time")
    download_savepath = __config.get("global", "download_savepath")
    analysis_savepath = __config.get("global", "analysis_savepath")
    download_msgqueue = __config.get("global", "download_msgqueue")


