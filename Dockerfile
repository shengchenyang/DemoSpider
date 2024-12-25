FROM nikolaik/python-nodejs:python3.10-nodejs20
RUN apt update && apt-get -y install libgl1-mesa-glx
WORKDIR /data/DemoSpider
COPY . .
RUN pip install -r requirements.txt
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo 'Asia/Shanghai' >/etc/timezone
CMD ["sh", "-c", "scrapy crawl ${spider_name}"]
