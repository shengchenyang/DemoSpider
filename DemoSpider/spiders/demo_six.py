import copy
from loguru import logger
from scrapy.http import Request
from ayugespidertools.Items import MongoDataItem
from DemoSpider.common.DataEnum import Table_Enum
from ayugespidertools.AyugeSpider import AyuSpider


"""
####################################################################################################
# collection_website: http://book.zongheng.com/ - 纵横中文网
# collection_content: 热榜文章排名 Demo 采集示例 - 异步存入 MongoDB (配置根据本地 settings 的 LOCAL_MYSQL_CONFIG 中取值)
# create_time: 2022-08-17
# explain:
# demand_code_prefix = ''
####################################################################################################
"""


class DemoSixSpider(AyuSpider):
    name = 'demo_six'
    allowed_domains = ['book.zongheng.com']
    start_urls = ['http://book.zongheng.com']

    # 初始化配置的类型
    settings_type = 'debug'
    custom_settings = {
        'LOG_LEVEL': 'ERROR',
        'ITEM_PIPELINES': {
            # 激活此项则数据会存储至 MongoDB
            'ayugespidertools.Pipelines.AyuTwistedMongoPipeline': 300,
        },
        'DOWNLOADER_MIDDLEWARES': {
            # 随机请求头
            'ayugespidertools.Middlewares.RandomRequestUaMiddleware': 400,
        },

        'CONCURRENT_REQUESTS': 64,
        'DOWNLOAD_DELAY': 0.1
    }

    def start_requests(self):
        """
        get 请求首页，获取项目列表数据
        """
        for page in range(0, 20):
            yield Request(
                url=f"http://book.zongheng.com/store/c0/c0/b0/u0/p{page}/v9/s9/t0/u0/i1/ALL.html",
                callback=self.parse_first,
                dont_filter=True
            )

    def parse_first(self, response):
        book_info_list = response.xpath('//div[@class="bookinfo"]')
        for book_info in book_info_list:
            book_name = book_info.xpath('div[@class="bookname"]/a/text()').extract_first("")
            book_href = book_info.xpath('div[@class="bookname"]/a/@href').extract_first("")
            book_intro = book_info.xpath('div[@class="bookintro"]/text()').extract_first("")
            # print(book_name, book_href, book_intro)

            Book_Info = dict()
            Book_Info['book_name'] = {'key_value': book_name, 'notes': '小说名称'}
            Book_Info['book_href'] = {'key_value': book_href, 'notes': '小说链接'}
            Book_Info['book_intro'] = {'key_value': book_intro, 'notes': '小说简介'}

            BookInfoItem = copy.deepcopy(MongoDataItem)
            BookInfoItem['alldata'] = Book_Info
            BookInfoItem['table'] = Table_Enum.book_info_list_table.value['value']
            BookInfoItem['mongo_update_rule'] = {"book_name": book_name}
            # logger.info(f"BookInfoItem: {BookInfoItem}")
            yield BookInfoItem
