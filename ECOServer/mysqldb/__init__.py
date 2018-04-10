#-*- coding: UTF-8 -*-
from mysqldb.connectionpool import ConnectionPool
from mysqldb.mysql_helper import MySQLHelper


__version__ = '1.0.0'
VERSION = tuple(map(int, __version__.split('.')))


__all__ = [
    'ConnectionPool', 'MySQLHelper'
]
