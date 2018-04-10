FROM python:3

MAINTAINER lichien@qq.com

RUN mkdir /usr/local/imagedownload/

RUN mkdir /usr/local/imagedownload/downloadServer

RUN mkdir /usr/local/imagedownload/downloadServer/files

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/local/imagedownload/downloadServer

CMD ["python","/usr/local/imagedownload/downloadServer/start_media_download_service.py"]
