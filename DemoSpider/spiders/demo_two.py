import json
from loguru import logger
from scrapy.http import Request
from ayugespidertools.Items import MongoDataItem
from DemoSpider.common.DataEnum import Table_Enum
from ayugespidertools.AyugeSpider import AyuSpider


"""
####################################################################################################
# collection_website: CSDN - 专业开发者社区
# collection_content: 热榜文章排名 Demo 采集示例 - 存入 MongoDB (配置根据本地 settings 的 LOCAL_MONGODB_CONFIG 中取值)
# create_time: 2022-08-02
# explain:
# demand_code_prefix = ''
####################################################################################################
"""


class DemoTwoSpider(AyuSpider):
    name = 'demo_two'
    allowed_domains = ['csdn.net']
    start_urls = ['https://blog.csdn.net/']

    # 初始化配置的类型
    settings_type = 'debug'
    custom_settings = {
        'ITEM_PIPELINES': {
            # 激活此项则数据会存储至 MongoDB
            'ayugespidertools.Pipelines.AyuFtyMongoPipeline': 300,
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

            """1. 兼容经典写法"""
            Aritle_Info = dict()
            Aritle_Info['article_detail_url'] = article_detail_url
            Aritle_Info['article_title'] = article_title
            Aritle_Info['comment_count'] = comment_count
            Aritle_Info['favor_count'] = favor_count
            Aritle_Info['nick_name'] = nick_name

            AritleInfoItem = MongoDataItem()
            # alldata 用于存储 mongo 的 Document 文档所需要的字段映射
            AritleInfoItem['alldata'] = Aritle_Info
            # table 为 mongo 的存储 Collection 集合的名称
            AritleInfoItem['table'] = Table_Enum.aritle_list_table.value['value']
            # mongo_update_rule 为查询数据是否存在的规则
            AritleInfoItem['mongo_update_rule'] = {"article_detail_url": article_detail_url}
            logger.info(f"AritleInfoItem: {AritleInfoItem}")
            yield AritleInfoItem

            """2.ayugespidertools 推荐的风格写法(更直观)"""
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

            """3.或者这样写"""
            item = {
                'alldata': {
                    'article_detail_url': article_detail_url,
                    'article_title': article_title,
                    'comment_count': comment_count,
                    'favor_count': favor_count,
                    'nick_name': nick_name,
                },
                'table': 'article_info_list',
                'mongo_update_rule': {"article_detail_url": article_detail_url},
            }
            yield item
