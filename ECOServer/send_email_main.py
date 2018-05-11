
from DataCollection.send_email import MongodbConn

if __name__ == '__main__':
    r = MongodbConn()
    r.start()