# coding=utf-8

import BaseModel
import argparse
import sys
import threading
import redis
sys.path.append("..")

from scrapyServer.config import ConfigHelper
from analysis.rule_level0_service import RuleServiceLevel0
from analysis.rule_level0_service import RuleServiceLevel1


ruleServiceLevel0 = RuleServiceLevel0(ConfigHelper.load_rule_time)

ruleServiceLevel1 = RuleServiceLevel1(ConfigHelper.load_rule_time)


def reload_rule():
    ruleServiceLevel0.load_rules(0)
    ruleServiceLevel1.load_rules(1)
    timer = threading.Timer(ConfigHelper.load_rule_time,reload_rule)
    timer.start()

if __name__ == "__main__":

    pool = redis.ConnectionPool(host=ConfigHelper.redisip, port=6379, db=ConfigHelper.redisdb)
    redis_server = redis.StrictRedis(connection_pool=pool)
    sub_job = "sendjob:SexyRule:1597605967290372"
    hset_keys = redis_server.hkeys(sub_job)
    for key in hset_keys:
        rel = redis_server.hget(sub_job, key)
        rel2 = int(rel.decode("utf-8"))
        print("ret = %d" % rel2)
        rel1 = rel2

    reload_rule()
    parser = argparse.ArgumentParser()
    # Optional arguments: input file.
    parser.add_argument(
        "-f","--input_file",
        help="Path to the configure file"
    )

    # Optional arguments: input threadnum.
    parser.add_argument(
        "-n", "--number",
        help="Threading Numbers",
        type=int
    )

    # Optional arguments: input threadnum.
    parser.add_argument(
        "-t", "--sleeptime",
        help="sleep time",
        type=int
    )

    args = parser.parse_args()

    if args.input_file == None:
        args.input_file = "scrapyServer/config.json"

    if args.number == None:
        args.number = 10

    if args.sleeptime == None:
        args.sleeptime = 10

    print(args)

    control = BaseModel.MainControl(args.input_file, args.sleeptime, args.number,ruleServiceLevel0,ruleServiceLevel1)
    control.startthread()