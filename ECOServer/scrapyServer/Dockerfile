FROM python:3

MAINTAINER lichien@qq.com

RUN mkdir /usr/local/scrapyServer/

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/local/scrapyServer/

CMD ["python","/usr/local/scrapyServer/flowcontrol.py"]
