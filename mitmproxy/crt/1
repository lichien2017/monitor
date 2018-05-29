FROM python:3

RUN pip install --upgrade pip

RUN pip install mitmproxy

RUN pip install redis==2.10.6

RUN mkdir /tmp/script

EXPOSE 8080 8081

CMD ["mitmproxy"]