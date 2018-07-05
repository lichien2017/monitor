
from DataCollection.Mysql import MongodbConn

if __name__ == '__main__':
    r = MongodbConn()
    r.start()