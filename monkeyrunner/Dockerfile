FROM python:2

MAINTAINER lichien@qq.com


RUN mkdir /usr/local/monkeyrunner/

RUN mkdir /usr/local/monkeyrunner/ecological

COPY ecological/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/local/monkeyrunner/ecological

CMD ["python","/usr/local/monkeyrunner/ecological/main.py"]
