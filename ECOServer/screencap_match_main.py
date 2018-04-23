
from screencap.screencap_match import ScreenCaptureMatch

from util import *
import  sys


def main():
    r = ScreenCaptureMatch()
    r.start()
    pass

if __name__ == "__main__" :
    SingleLogger().log.debug("测试")
    main()
