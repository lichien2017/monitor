from pymongo import MongoClient
from util import *
import datetime
import redis
import json
from bson import ObjectId
from bson.int64 import Int64
time_format = "%Y-%m-%d %H:%M:%S"
interval = 10 #10分钟间隔
DAYS = -1 # 与今天的差异，0 标示处理当天，-1标示处理前一天


from analysis.rule_level0_service import RuleServiceLevel0
from analysis.rule_level0_service import RuleServiceLevel1




if __name__ == '__main__':

    _client = MongoClient(ConfigHelper.mongodbip, ConfigHelper.mongodbport)
    _database = _client["crawlnews"]

    ruleServiceLevel0 = RuleServiceLevel0(ConfigHelper.load_rule_time)
    ruleServiceLevel0.load_rules(0)
    ruleServiceLevel1 = RuleServiceLevel1(ConfigHelper.load_rule_time)
    ruleServiceLevel1.load_rules(1)
    ruleServiceLevel1.execute_all()

    date = LocalTime.from_today(-7)
    date_str = date.strftime("%Y%m%d")
    rows = _database["originnews" + date_str].find()
    for row in rows:
        msg = {"res_id": "%s" % row["identity"],
               "time": date_str}
        SingleLogger().log.debug("Rule0server.execute_all == %s", json.dumps(msg))
        ruleServiceLevel0.execute_all(json.dumps(msg))  # 插入的数据格式为json
        SingleLogger().log.debug("Rule1server.add_resource_to_all_queue == %s", json.dumps(msg))
        ruleServiceLevel1.add_resource_to_all_queue(json.dumps(msg))

    pass