import urllib.request
import requests
from util.log import SingleLogger


class Http():
    @staticmethod
    def get(url,referer=None):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36',
            'Accept': 'text/html;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'gzip',
            'Connection': 'close',
            'referer':referer
            }

        response = requests.get(url,headers=headers)
        if response.status_code == 200 :
            SingleLogger().log.debug("==========response.text===========>%s" % response.text)
            SingleLogger().log.debug("==========response.content===========>%s" % response.content)

            return response.content
        else:
            return ""
        pass
    pass