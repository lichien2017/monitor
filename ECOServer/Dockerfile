FROM python:3

MAINTAINER lichien@qq.com

RUN mkdir /usr/local/ECOServer/

RUN mkdir /usr/local/ECOServer/files

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/local/ECOServer/

CMD ["python","/usr/local/ECOServer/flowcontrol.py"]
