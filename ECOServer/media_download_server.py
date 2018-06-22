
from mediaDownloadServer.media_download import MediaDownload

THREAD_COUNT = 5 # 启动多个线程来处理
if __name__ == '__main__':
    for i in range(THREAD_COUNT): # 启动多个线程来处理
        r = MediaDownload()
        r.start()
        pass