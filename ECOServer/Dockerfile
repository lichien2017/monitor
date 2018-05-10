FROM python:3

MAINTAINER lichien@qq.com

RUN mkdir /usr/local/ECOServer/

COPY requirements.txt .
COPY crontab /tmp/crontab
RUN yes | cp -rf /tmp/crontab /etc/crontab
RUN apt-get update && apt-get install -y cron vim
RUN service cron restart
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/local/ECOServer/

CMD ["python","/usr/local/ECOServer/flowcontrol.py"]
