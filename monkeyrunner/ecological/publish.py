import redis

pool = redis.ConnectionPool(host='192.168.10.176', port=6379, db=0)
r = redis.StrictRedis(connection_pool=pool)
while True:
    input = raw_input("publish:")
    if input == 'over':
        print '停止发布'
        break;
    r.publish('spub', input)  