import pandas
from loguru import logger
from scrapy.http import Request
from ayugespidertools.Items import MysqlDataItem
from DemoSpider.common.DataEnum import TableEnum
from ayugespidertools.AyugeSpider import AyuSpider
from ayugespidertools.common.Utils import ToolsForAyu


"""
####################################################################################################
# collection_website: http://book.zongheng.com/ - 纵横中文网
# collection_content: 纵横中文网小说书库采集 - 异步存入 Mysql (配置根据本地 settings 的 LOCAL_MYSQL_CONFIG 中取值)
# create_time: 2022-07-30
# explain:
# demand_code_prefix = ''
####################################################################################################
"""


class DemoFiveSpider(AyuSpider):
    name = 'demo_five'
    allowed_domains = ['book.zongheng.com']
    start_urls = ['http://book.zongheng.com']

    # 数据库表的枚举信息
    custom_table_enum = TableEnum
    # 初始化配置的类型
    settings_type = 'debug'
    custom_settings = {
        'LOG_LEVEL': 'ERROR',
        # 数据表的前缀名称，用于标记属于哪个项目
        'MYSQL_TABLE_PREFIX': "demo5_",
        'ITEM_PIPELINES': {
            # 激活此项则数据会存储至 Mysql
            'ayugespidertools.Pipelines.AyuTwistedMysqlPipeline': 300,
        },
        'DOWNLOADER_MIDDLEWARES': {
            # 随机请求头
            'ayugespidertools.Middlewares.RandomRequestUaMiddleware': 400,
        },
        'CONCURRENT_REQUESTS': 64,
        'DOWNLOAD_DELAY': 0.01
    }

    # 打开 mysql 引擎开关，用于数据入库前更新逻辑判断
    mysql_engine_enabled = True

    def start_requests(self):
        """
        get 请求首页，获取项目列表数据
        """
        for page in range(1, 128):
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
            # logger.info(f"BookInfoItem: {BookInfoItem}")

            # 数据入库逻辑
            try:
                # 测试 mysql_engine 的去重功能
                sql = '''select `id` from `{}` where `book_name` = "{}" limit 1'''.format(
                    self.custom_settings.get('MYSQL_TABLE_PREFIX', '') + TableEnum.book_info_list_table.value['value'], book_name)
                df = pandas.read_sql(sql, self.mysql_engine)

                # 如果为空，说明此数据不存在于数据库，则新增
                if df.empty:
                    yield BookInfoItem

                # 如果已存在，1). 若需要更新，请自定义更新数据结构和更新逻辑；2). 若不用更新，则跳过即可。
                else:
                    logger.debug(f"标题为 “{book_name}“ 的数据已存在")

            except Exception as e:
                if any(["1146" in str(e), "1054" in str(e), "doesn't exist" in str(e)]):
                    yield BookInfoItem
                else:
                    logger.error(f"请查看数据库链接或网络是否通畅！Error: {e}")
