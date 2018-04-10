# coding=utf-8

from scrapyServer.BaseModel import MainControl
import argparse
import sys
import threading

from scrapyServer.config import ConfigHelper
# from analysis.rule_level0_service import RuleServiceLevel0
# from analysis.rule_level0_service import RuleServiceLevel1
#
#
# ruleServiceLevel0 = RuleServiceLevel0(ConfigHelper.load_rule_time)
# ruleServiceLevel0.load_rules(0)
# ruleServiceLevel1 = RuleServiceLevel1(ConfigHelper.load_rule_time)
# ruleServiceLevel1.load_rules(1)
#
# def reload_rule():
#     ruleServiceLevel0.load_rules(0)
#     ruleServiceLevel1.load_rules(1)
#     timer = threading.Timer(ConfigHelper.load_rule_time,reload_rule)
#     timer.start()

if __name__ == "__main__":
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

    control = MainControl(args.input_file, args.sleeptime, args.number)
    control.startthread()