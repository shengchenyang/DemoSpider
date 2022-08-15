import pandas
from loguru import logger
from scrapy.http import Request
from ayugespidertools.Items import DataItem
from DemoSpider.common.DataEnum import Table_Enum
from ayugespidertools.AyugeSpider import AyuSpider


"""
####################################################################################################
# collection_website: http://book.zongheng.com/ - 纵横中文网
# collection_content: 热榜文章排名 Demo 采集示例 - 异步存入 Mysql (配置根据本地 settings 的 LOCAL_MYSQL_CONFIG 中取值)
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
    custom_table_enum = Table_Enum
    # 初始化配置的类型
    settings_type = 'debug'
    custom_settings = {
        # 数据表的前缀名称，用于标记属于哪个项目
        'MYSQL_TABLE_PREFIX': "demo_",
        'ITEM_PIPELINES': {
            # 激活此项则数据会存储至 Mysql
            'ayugespidertools.Pipelines.AyuTwistedMysqlPipeline': 300,
        },

        'DOWNLOADER_MIDDLEWARES': {
            # 随机请求头
            'ayugespidertools.Middlewares.RandomRequestUaMiddleware': 400,
        },

        'CONCURRENT_REQUESTS': 64,
        'DOWNLOAD_DELAY': 0.1
    }

    # 打开 mysql 引擎开关，用于数据入库前更新逻辑判断
    mysql_engine_off = True

    def start_requests(self):
        """
        get 请求首页，获取项目列表数据
        """
        for page in range(0, 200):
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

            BookInfoItem = DataItem()
            BookInfoItem['alldata'] = Book_Info
            BookInfoItem['table'] = Table_Enum.book_info_list_table.value['value']
            # logger.info(f"BookInfoItem: {BookInfoItem}")
            # yield BookInfoItem

            # 数据入库逻辑
            try:
                # 测试 mysql_engine 的去重功能
                sql = '''select `id` from `{}` where `book_name` = "{}" limit 1'''.format(self.custom_settings['MYSQL_TABLE_PREFIX'] + Table_Enum.book_info_list_table.value['value'], book_name)
                df = pandas.read_sql(sql, self.mysql_engine)

                # 如果为空，说明此数据不存在于数据库，则新增
                if df.empty:
                    yield BookInfoItem

                # 如果已存在，1). 若需要更新，请自定义更新数据结构和更新逻辑；2). 若不用更新，则跳过即可。
                else:
                    logger.debug(f"标题为 ”{book_name}“ 的数据已存在，请自定义更新逻辑")

            except Exception as e:
                if any(["1146" in str(e), "doesn't exist" in str(e)]):
                    yield BookInfoItem
                else:
                    logger.error("请查看数据库链接或网络是否通畅！")
