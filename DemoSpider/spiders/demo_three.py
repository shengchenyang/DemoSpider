import json
import pandas
from loguru import logger
from scrapy.http import Request
from ayugespidertools.Items import DataItem
from DemoSpider.common.DataEnum import Table_Enum
from ayugespidertools.AyugeSpider import AyuSpider


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
            article_detail_url = curr_data['articleDetailUrl']
            article_title = curr_data['articleTitle']
            comment_count = curr_data['commentCount']
            favor_count = curr_data['favorCount']
            nick_name = curr_data['nickName']
            logger.info(f"article data: {article_detail_url, article_title, comment_count, favor_count, nick_name}")

            Aritle_Info = dict()
            Aritle_Info['article_detail_url'] = {'key_value': article_detail_url, 'notes': '文章详情链接'}
            Aritle_Info['article_title'] = {'key_value': article_title, 'notes': '文章标题'}
            Aritle_Info['comment_count'] = {'key_value': comment_count, 'notes': '文章评论数量'}
            Aritle_Info['favor_count'] = {'key_value': favor_count, 'notes': '文章收藏数量'}
            Aritle_Info['nick_name'] = {'key_value': nick_name, 'notes': '文章作者昵称'}

            AritleInfoItem = DataItem()
            AritleInfoItem['alldata'] = Aritle_Info
            AritleInfoItem['table'] = Table_Enum.aritle_list_table.value['value']
            logger.info(f"AritleInfoItem: {AritleInfoItem}")
            # yield AritleInfoItem

            # 旧脚本方便地改写为 ayugespidertools 的示例
            '''
            item = {
                'article_detail_url': article_detail_url,
                'article_title': article_title,
                'comment_count': comment_count,
                'favor_count': favor_count,
                'nick_name': nick_name,
                # 兼容旧写法，但是要添加 table 字段(即需要存储的表格名称，注意：是去除表格前缀的表名,
                # 比如表为 demo_article_info_list，前缀为 demo_，则 table 名为 article_info_list)
                'table': 'article_info_list',
            }
            yield item

            # 或者这样写
            item = dict()
            item['article_detail_url'] = article_detail_url
            item['article_title'] = article_title
            item['comment_count'] = comment_count
            item['favor_count'] = favor_count
            item['nick_name'] = nick_name
            item['table'] = 'article_info_list'
            yield item
            '''

            try:
                # 测试 mysql_engine 的功能
                sql = '''select `id` from `{}` where `article_detail_url` = "{}" limit 1'''.format(self.custom_settings.get('MYSQL_TABLE_PREFIX', '') + Table_Enum.aritle_list_table.value['value'], article_detail_url)
                df = pandas.read_sql(sql, self.mysql_engine)

                # 如果为空，说明此数据不存在于数据库，则新增
                if df.empty:
                    yield AritleInfoItem

                # 如果已存在，1). 若需要更新，请自定义更新数据结构和更新逻辑；2). 若不用更新，则跳过即可。
                else:
                    logger.debug(f"标题为 ”{article_title}“ 的数据已存在，请自定义更新逻辑")

            except Exception:
                yield AritleInfoItem
