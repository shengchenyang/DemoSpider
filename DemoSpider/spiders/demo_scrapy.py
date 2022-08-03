import scrapy


"""
####################################################################################################
# collection_website: None
# collection_content: None
# create_time: 2022-07-30
# explain: 只是为了展示 scrapy 的默认生成的 spider 的样式及默认用法
# demand_code_prefix = ''
####################################################################################################
"""


class DemoScrapySpider(scrapy.Spider):
    name = 'demo_scrapy'
    allowed_domains = ['baidu.com']
    start_urls = ['http://www.baidu.com/']

    def parse(self, response):
        pass
