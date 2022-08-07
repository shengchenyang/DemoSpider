import json
from loguru import logger
from scrapy.http import Request
from ayugespidertools.Items import MongoDataItem
from DemoSpider.common.DataEnum import Table_Enum
from ayugespidertools.AyugeSpider import AyuSpider


"""
####################################################################################################
# collection_website: CSDN - 专业开发者社区
# collection_content: 热榜文章排名 Demo 采集示例 - 存入 MongoDB (配置根据 consul 的应用管理中心中取值)
# create_time: 2022-08-02
# explain:
# demand_code_prefix = ''
####################################################################################################
"""


class DemoFourSpider(AyuSpider):
    name = 'demo_four'
    allowed_domains = ['blog.csdn.net']
    start_urls = ['https://blog.csdn.net/']

    # 初始化配置的类型
    settings_type = 'debug'
    custom_settings = {
        # 是否开启 consul 的应用管理中心取值的功能(也需要设置 CONSUL_CONF 的值，本示例在 settings 中配置)
        'APP_CONF_MANAGE': True,
        'ITEM_PIPELINES': {
            # 激活此项则数据会存储至 MongoDB
            'ayugespidertools.Pipelines.AyuALSMongoPipeline': 300,
        },
        'DOWNLOADER_MIDDLEWARES': {
            # 随机请求头
            'ayugespidertools.Middlewares.RandomRequestUaMiddleware': 400,
        },
    }

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

            """ayugespidertools 推荐的风格写法(更直观)"""
            Aritle_Info = dict()
            Aritle_Info['article_detail_url'] = {'key_value': article_detail_url, 'notes': '文章详情链接'}
            Aritle_Info['article_title'] = {'key_value': article_title, 'notes': '文章标题'}
            Aritle_Info['comment_count'] = {'key_value': comment_count, 'notes': '文章评论数量'}
            Aritle_Info['favor_count'] = {'key_value': favor_count, 'notes': '文章收藏数量'}
            Aritle_Info['nick_name'] = {'key_value': nick_name, 'notes': '文章作者昵称'}

            AritleInfoItem = MongoDataItem()
            AritleInfoItem['alldata'] = Aritle_Info
            AritleInfoItem['table'] = Table_Enum.aritle_list_table.value['value']
            AritleInfoItem['mongo_update_rule'] = {"article_detail_url": article_detail_url}
            logger.info(f"AritleInfoItem: {AritleInfoItem}")
            yield AritleInfoItem

