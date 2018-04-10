#-*- coding: UTF-8 -*-
import configparser
import os

class ConfigHelper:
    # mysqldb.logger.setLevel('DEBUG')
    __config = configparser.ConfigParser()
    localDir = os.path.dirname(__file__)
    __config.read(localDir+"/config.ini")
    # mysql_ip = __config.get("mysql", "mysql_ip")
    # mysql_user = __config.get("mysql", "mysql_user")
    # mysql_pwd = __config.get("mysql", "mysql_pwd")
    # mysql_db = __config.get("mysql", "mysql_db")
    mongodbip = __config.get("mongodb", "mongodbip")
    redisip = __config.get("redis", "redisip")
    redisdb = __config.get("redis", "redisdb")
    image_savepath = __config.get("global", "image_savepath")
    download_msgqueue = __config.get("global", "download_msgqueue")


