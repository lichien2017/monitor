from mysqldb.connectionpool import ConnectionPool
from util.config import ConfigHelper


class MySQLHelper:

    config = {'host': ConfigHelper.mysql_ip, 'user': ConfigHelper.mysql_user,
              'password': ConfigHelper.mysql_pwd, 'database': ConfigHelper.mysql_db,
              'autocommit': 1, 'charset': 'utf8'}
    ### Create a connection pool with 2 connection in it
    pool_connection = ConnectionPool(size=2, name='pool1', **config)