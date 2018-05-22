from device.getPush import getPush
from threading import Thread
import time
if __name__ == '__main__':
    r = getPush()
    r.Run()
    while True :
        time.sleep(5)
        pass