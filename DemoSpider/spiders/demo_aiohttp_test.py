from DemoSpider.settings import logger
from ayugespidertools.Items import MysqlDataItem
from DemoSpider.common.DataEnum import TableEnum
from ayugespidertools.AyugeSpider import AyuSpider
from ayugespidertools.common.Utils import ToolsForAyu
from ayugespidertools.AyuRequest import AiohttpRequest, AioFormRequest


"""
####################################################################################################
# collection_website: http://book.zongheng.com/ - 纵横中文网
# collection_content: 纵横中文网小说书库采集 - 测试 aiohttp 请求的功能示例
# create_time: 2022-09-01
# explain:
# demand_code_prefix = ''
####################################################################################################
"""


class DemoAiohttpTestSpider(AyuSpider):
    name = 'demo_aiohttp_test'
    allowed_domains = ['book.zongheng.com']
    start_urls = ['http://book.zongheng.com']

    # 数据库表的枚举信息
    custom_table_enum = TableEnum
    # 初始化配置的类型
    settings_type = 'debug'
    custom_settings = {
        'LOG_LEVEL': 'ERROR',
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        'DOWNLOADER_MIDDLEWARES': {
            # 随机请求头
            'ayugespidertools.Middlewares.RandomRequestUaMiddleware': 400,
            # 替换请求的中间件
            'ayugespidertools.DownloaderMiddlewares.AiohttpMiddleware': 543,
            # 'ayugespidertools.DownloaderMiddlewares.AiohttpAsyncMiddleware': 543,
        },
        'CONCURRENT_REQUESTS': 100,
        'DOWNLOAD_DELAY': 0.001
    }

    def start_requests(self):
        """
        get 请求首页，获取项目列表数据
        """
        for page in range(1, 100):
            yield AiohttpRequest(
                url=f"http://book.zongheng.com/store/c0/c0/b0/u0/p{page}/v9/s9/t0/u0/i1/ALL.html",
                callback=self.parse_first,
                meta={
                    "meta_data": "这是用来测试 parse_first meta 的功能",
                    "aiohttp_args": {
                        "timeout": 10,
                        "tmp": "tmp_data",
                    }
                },
                dont_filter=True
            )

    def parse_first(self, response):
        book_info_list = ToolsForAyu.extract_with_xpath(response=response, query='//div[@class="bookinfo"]', return_selector=True)
        for book_info in book_info_list:
            book_name = ToolsForAyu.extract_with_xpath(response=book_info, query='div[@class="bookname"]/a/text()')
            book_href = ToolsForAyu.extract_with_xpath(response=book_info, query='div[@class="bookname"]/a/@href')
            book_intro = ToolsForAyu.extract_with_xpath(response=book_info, query='div[@class="bookintro"]/text()')
            # print(book_name, book_href, book_intro)

            book_info = {
                "book_name": {'key_value': book_name, 'notes': '小说名称'},
                "book_href": {'key_value': book_href, 'notes': '小说链接'},
                "book_intro": {'key_value': book_intro, 'notes': '小说简介'},
            }

            BookInfoItem = MysqlDataItem(
                alldata=book_info,
                table=TableEnum.book_info_list_table.value['value'],
            )
            logger.info(f"BookInfoItem: {BookInfoItem}")
