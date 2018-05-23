#-*- coding: UTF-8 -*-
from analysis.rule import Rule
from analysis.rule_level1 import BaseLevel1Rule
from analysis.rule import RuleFactory
from analysis.rule_level0 import ColumnRule
from analysis.rule_level0 import KeyWordRule
from analysis.rule_level1 import XueXingBaoLiRule
from analysis.rule_level1 import SexyRule
from analysis.rule_level1 import PoliticalRule
from analysis.rule_level1 import ZongJiaoRule
from analysis.rule_level1 import BiaoTiDangRule
from analysis.rule_level1 import ScreenCapORCRule
from analysis.rule_level0 import WeMediaRule
__version__ = '1.0.0'
VERSION = tuple(map(int, __version__.split('.')))


__all__ = [
    'RuleFactory', 'ColumnRule','KeyWordRule','BaseLevel1Rule','XueXingBaoLiRule','SexyRule','PoliticalRule',
    'ZongJiaoRule','BiaoTiDangRule','ScreenCapORCRule','WeMediaRule'
]
