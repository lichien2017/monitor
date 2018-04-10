from analysis.rule_level0_service import RuleServiceLevel0
from analysis.rule_level0_service import RuleServiceLevel1
import threading
import hashlib
import time
from config import ConfigHelper

ruleServiceLevel0 = RuleServiceLevel0(ConfigHelper.load_rule_time)
ruleServiceLevel1 = RuleServiceLevel1(ConfigHelper.load_rule_time)

def reload_rule():
    ruleServiceLevel0.load_rules(0)
    ruleServiceLevel1.load_rules(1)
    timer = threading.Timer(ConfigHelper.load_rule_time,reload_rule)
    timer.start()

if __name__ == "__main__":
    print('ruleService准备启动')
    reload_rule()
    # m = hashlib.md5()
    # m.update('ruleService准备启动1232132131321'.encode("utf-8"))
    # print(m.hexdigest())
    # rule_service_level = RuleServiceLevel1()
    # rule_service_level.load_rules()
    # rule_service_level.add_resource_to_all_queue("20180123V0XX3D00")

    print('ruleService启动成功')