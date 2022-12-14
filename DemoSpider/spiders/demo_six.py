# from loguru import logger
from scrapy.http import Request
from ayugespidertools.Items import MongoDataItem
from DemoSpider.common.DataEnum import TableEnum
from ayugespidertools.AyugeSpider import AyuSpider
from ayugespidertools.common.Utils import ToolsForAyu


"""
####################################################################################################
# collection_website: http://book.zongheng.com/ - 纵横中文网
# collection_content: 纵横中文网小说书库采集 - 异步存入 MongoDB (配置根据本地 settings 的 LOCAL_MYSQL_CONFIG 中取值)
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
        'MONGODB_COLLECTION_PREFIX': "demo6_",
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
        for page in range(1, 3):
            yield Request(
                url=f"http://book.zongheng.com/store/c0/c0/b0/u0/p{page}/v9/s9/t0/u0/i1/ALL.html",
                callback=self.parse_first,
                dont_filter=True
            )

    def parse_first(self, response):
        book_info_list = ToolsForAyu.extract_with_xpath(response=response, query='//div[@class="bookinfo"]', return_selector=True)
        for book_info in book_info_list:
            book_name = ToolsForAyu.extract_with_xpath(response=book_info, query='div[@class="bookname"]/a/text()')
            book_href = ToolsForAyu.extract_with_xpath(response=book_info, query='div[@class="bookname"]/a/@href')
            book_intro = ToolsForAyu.extract_with_xpath(response=book_info, query='div[@class="bookintro"]/text()')

            book_info = {
                "book_name": {'key_value': book_name, 'notes': '小说名称'},
                "book_href": {'key_value': book_href, 'notes': '小说链接'},
                "book_intro": {'key_value': book_intro, 'notes': '小说简介'},
            }

            BookInfoItem = MongoDataItem(
                # alldata 用于存储 mongo 的 Document 文档所需要的字段映射
                alldata=book_info,
                # table 为 mongo 的存储 Collection 集合的名称
                table=TableEnum.book_info_list_table.value['value'],
                # mongo_update_rule 为查询数据是否存在的规则
                mongo_update_rule={"book_name": book_name},
            )

            # logger.info(f"BookInfoItem: {BookInfoItem}")
            yield BookInfoItem
