import json
import pandas
from loguru import logger
from scrapy.http import Request
from ayugespidertools.Items import MysqlDataItem
from DemoSpider.common.DataEnum import Table_Enum
from ayugespidertools.AyugeSpider import AyuSpider
from ayugespidertools.common.Utils import ToolsForAyu


"""
####################################################################################################
# collection_website: CSDN - 专业开发者社区
# collection_content: 热榜文章排名 Demo 采集示例 - 存入 Mysql (配置根据 consul 的应用管理中心中取值)
# create_time: 2022-08-07
# explain:
# demand_code_prefix = ''
####################################################################################################
"""


class DemoThreeSpider(AyuSpider):
    name = 'demo_three'
    allowed_domains = ['blog.csdn.net']
    start_urls = ['https://blog.csdn.net/']

    # 数据库表的枚举信息
    custom_table_enum = Table_Enum
    # 初始化配置的类型
    settings_type = 'debug'
    custom_settings = {
        # 是否开启 consul 的应用管理中心取值的功能(也需要设置 CONSUL_CONF 的值，本示例在 settings 中配置)
        'APP_CONF_MANAGE': True,
        # 数据表的前缀名称，用于标记属于哪个项目
        'MYSQL_TABLE_PREFIX': "demo3_",
        'ITEM_PIPELINES': {
            # 激活此项则数据会存储至 Mysql
            'ayugespidertools.Pipelines.AyuFtyMysqlPipeline': 300,
        },

        'DOWNLOADER_MIDDLEWARES': {
            # 随机请求头
            'ayugespidertools.Middlewares.RandomRequestUaMiddleware': 400,
        },
    }

    # 打开 mysql 引擎开关，用于数据入库前更新逻辑判断
    mysql_engine_off = True

    def start_requests(self):
        """
        get 请求首页，获取项目列表数据
        """
        yield Request(
            url="https://blog.csdn.net/phoenix/web/blog/hot-rank?page=0&pageSize=25&type=",
            callback=self.parse_first,
            headers={
                'referer': 'https://blog.csdn.net/rank/list',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
            },
            dont_filter=True
        )

    def parse_first(self, response):
        data_list = json.loads(response.text)['data']
        for curr_data in data_list:
            article_detail_url = ToolsForAyu.extract_with_json(json_data=curr_data, query="articleDetailUrl")
            article_title = ToolsForAyu.extract_with_json(json_data=curr_data, query="articleTitle")
            comment_count = ToolsForAyu.extract_with_json(json_data=curr_data, query="commentCount")
            favor_count = ToolsForAyu.extract_with_json(json_data=curr_data, query="favorCount")
            nick_name = ToolsForAyu.extract_with_json(json_data=curr_data, query="nickName")

            article_info = {
                "article_detail_url": {'key_value': article_detail_url, 'notes': '文章详情链接'},
                "article_title": {'key_value': article_title, 'notes': '文章标题'},
                "comment_count": {'key_value': comment_count, 'notes': '文章评论数量'},
                "favor_count": {'key_value': favor_count, 'notes': '文章赞成数量'},
                "nick_name": {'key_value': nick_name, 'notes': '文章作者昵称'}
            }

            AritleInfoItem = MysqlDataItem(
                alldata=article_info,
                table=Table_Enum.aritle_list_table.value['value'],
            )
            logger.info(f"AritleInfoItem: {AritleInfoItem}")
            # yield AritleInfoItem

            try:
                # 测试 mysql_engine 的功能
                sql = '''select `id` from `{}` where `article_detail_url` = "{}" limit 1'''.format(self.custom_settings.get('MYSQL_TABLE_PREFIX', '') + Table_Enum.aritle_list_table.value['value'], article_detail_url)
                df = pandas.read_sql(sql, self.mysql_engine)

                # 如果为空，说明此数据不存在于数据库，则新增
                if df.empty:
                    yield AritleInfoItem

                # 如果已存在，1). 若需要更新，请自定义更新数据结构和更新逻辑；2). 若不用更新，则跳过即可。
                else:
                    logger.debug(f"标题为 ”{article_title}“ 的数据已存在")

            except Exception:
                yield AritleInfoItem
