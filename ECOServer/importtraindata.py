# coding=utf-8

import os
from mysqldb.mysql_helper import MySQLHelper
from DataCollection.data_collection import Collector
import argparse
import json
from DataCollection.filterflag import *
import jieba
import time

from DataCollection.langconv import *

def T2S(line):
    # 转换繁体到简体
    line = Converter('zh-hans').convert(line.decode('utf-8'))
    line = line.encode('utf-8')
    return line

def S2T(line):
    # 转换简体到繁体
    line = Converter('zh-hant').convert(line.decode('utf-8'))
    line = line.encode('utf-8')
    return line

def getsrc(config):
    collect = Collector()
    news = collect.news_reader(config["rule_tag"])
    #逐条枚举数据,生成文件

    filename = "%s/%f.txt"%(config["train_data_dir"],time.time())
    with open(filename, "w") as f:
        for idx, (item,content) in enumerate(news):
            print("idx is:", idx)
            print("item is:", item)
            #print("content is:", content)

            linetext = content.strip()
            linetext = filter_tags(linetext)
            linetext = T2S(linetext)
            #print('linetext is:', linetext)
            seg_list = jieba.cut(linetext)
            # ' '.join(seg_list)
            #print('doc is:', ' '.join(seg_list))
            writelinetext = "%s\t%s\n" % (config["train_tag"], ' '.join(seg_list))
            print("linetext is: ", writelinetext)
            f.write(writelinetext)

def getdata():
    collect = Collector()
    news = collect.news_reader2("tag")

    filename = "normal_z.txt"
    with open(filename, "w") as f:
        for idx, content in enumerate(news):
            print("idx is:", idx)
            print("item is:", content)
            linetext = content.strip()
            linetext = filter_tags(linetext)
            print("linetext is:", linetext)
            #linetext = T2S(linetext)
            # print('linetext is:', linetext)
            seg_list = jieba.cut(linetext)
            # ' '.join(seg_list)
            # print('doc is:', ' '.join(seg_list))
            writelinetext = "%s\t%s\n" % ("normal", ' '.join(seg_list))
            print("linetext is: ", writelinetext)
            f.write(writelinetext)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Required arguments: input file.
    parser.add_argument(
        "configurepath",
        nargs='?',
        default="DataCollection/trainconfig.ini",
        help="Path to the configure file"
    )

    args = parser.parse_args()

    #print(os.path.dirname(args.configurepath))
    #os.makedirs(os.path.dirname(args.configurepath))
    # localDir = os.path.dirname(__file__)
    # args.configurepath = localDir + "/DataCollection/config_local.ini"
    assert os.path.exists(args.configurepath), "The configure model file not exist."




    with open(args.configurepath, "r") as f:
        jsonconfig = json.load(f)
        getsrc(jsonconfig["text_political"])
        getsrc(jsonconfig["text_sexy"])
        #getdata()
