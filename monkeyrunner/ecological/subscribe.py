# coding=utf-8  
''''' 
Created on 2015-9-9 

@author: kwsy 
'''
import redis

pool = redis.ConnectionPool(host='192.168.10.176', port=6379, db=0)
r = redis.StrictRedis(connection_pool=pool)
p = r.pubsub()
p.subscribe('excelFile')
for item in p.listen():
    print item
    if item['type'] == 'message':
        data = item['data']
        r.set('s', 32)
        print data
        if item['data'] == 'over':
            break;
p.unsubscribe('spub')
print '取消订阅'  