import json
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
        # mysql db 连接池配置
        'POOL_DB_CONFIG': {
            'maxconnections': 5,
            'blocking': True,
        },
        'ITEM_PIPELINES': {
            # 激活此项则数据会存储至 Mysql
            'ayugespidertools.Pipelines.AyuTurboMysqlPipeline': 300,
        },

        'DOWNLOADER_MIDDLEWARES': {
            # 随机请求头
            'ayugespidertools.Middlewares.RandomRequestUaMiddleware': 400,
        },

        'CONCURRENT_REQUESTS': 100,
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
            yield BookInfoItem

        # data_list = json.loads(response.text)['data']
        # for curr_data in data_list:
        #     article_detail_url = curr_data['articleDetailUrl']
        #     article_title = curr_data['articleTitle']
        #     comment_count = curr_data['commentCount']
        #     favor_count = curr_data['favorCount']
        #     nick_name = curr_data['nickName']
        #     logger.info(f"article data: {article_detail_url, article_title, comment_count, favor_count, nick_name}")
        #
        #     Aritle_Info = dict()
        #     Aritle_Info['article_detail_url'] = {'key_value': article_detail_url, 'notes': '文章详情链接'}
        #     Aritle_Info['article_title'] = {'key_value': article_title, 'notes': '文章标题'}
        #     Aritle_Info['comment_count'] = {'key_value': comment_count, 'notes': '文章评论数量'}
        #     Aritle_Info['favor_count'] = {'key_value': favor_count, 'notes': '文章收藏数量'}
        #     Aritle_Info['nick_name'] = {'key_value': nick_name, 'notes': '文章作者昵称'}
        #
        #     AritleInfoItem = DataItem()
        #     AritleInfoItem['alldata'] = Aritle_Info
        #     AritleInfoItem['table'] = Table_Enum.aritle_list_table.value['value']
        #     logger.info(f"AritleInfoItem: {AritleInfoItem}")
        #     # yield AritleInfoItem
        #
        #     # 数据入库逻辑
        #     try:
        #         # 测试 mysql_engine 的去重功能
        #         sql = '''select `id` from `{}` where `article_detail_url` = "{}" limit 1'''.format(
        #             self.custom_settings['MYSQL_TABLE_PREFIX'] + Table_Enum.aritle_list_table.value['value'],
        #             article_detail_url)
        #         df = pandas.read_sql(sql, self.mysql_engine)
        #
        #         # 如果为空，说明此数据不存在于数据库，则新增
        #         if df.empty:
        #             yield AritleInfoItem
        #
        #         # 如果已存在，1). 若需要更新，请自定义更新数据结构和更新逻辑；2). 若不用更新，则跳过即可。
        #         else:
        #             logger.debug(f"标题为 ”{article_title}“ 的数据已存在，请自定义更新逻辑")
        #
        #     except Exception as e:
        #         if any(["1146" in str(e), "doesn't exist" in str(e)]):
        #             yield AritleInfoItem
        #         else:
        #             logger.error("请查看数据库链接或网络是否通畅！")
