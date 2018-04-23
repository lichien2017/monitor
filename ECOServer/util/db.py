# from mysqldb import *
from util.config import ConfigHelper
# from util.log import Singleton
import redis

class RedisHelper():
    connection_pool = redis.ConnectionPool(host=ConfigHelper.redisip, port=ConfigHelper.redisport, db=ConfigHelper.redisdb)
    # redis = redis.Redis(connection_pool=connection_pool)
    strict_redis = redis.StrictRedis(connection_pool=connection_pool)
