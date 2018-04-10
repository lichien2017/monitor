from analysis.rule_level0_service import RuleServiceLevel0
from analysis.rule_level0_service import RuleServiceLevel1
import time
import hashlib

if __name__ == "__main__":
    print('ruleService准备启动')

    m = hashlib.md5()
    m.update('ruleService准备启动1232132131321'.encode("utf-8"))
    print(m.hexdigest())
    rule_service_level = RuleServiceLevel1()
    rule_service_level.load_rules()
    rule_service_level.add_resource_to_all_queue("20180123V0XX3D00")

    print('ruleService启动成功')