import json
from loguru import logger
from scrapy.http import Request
from ayugespidertools.Items import MongoDataItem
from DemoSpider.common.DataEnum import Table_Enum
from ayugespidertools.AyugeSpider import AyuSpider
from ayugespidertools.common.Utils import ToolsForAyu


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
            },
            dont_filter=True
        )

    def parse_first(self, response):
        data_list = ToolsForAyu.extract_with_json(json_data=response.json(), query="data")
        for curr_data in data_list:
            article_detail_url = ToolsForAyu.extract_with_json(json_data=curr_data, query="articleDetailUrl")
            article_title = ToolsForAyu.extract_with_json(json_data=curr_data, query="articleTitle")
            comment_count = ToolsForAyu.extract_with_json(json_data=curr_data, query="commentCount")
            favor_count = ToolsForAyu.extract_with_json(json_data=curr_data, query="favorCount")
            nick_name = ToolsForAyu.extract_with_json(json_data=curr_data, query="nickName")
            logger.info(f"article data: {article_detail_url, article_title, comment_count, favor_count, nick_name}")

            """1. ayugespidertools 推荐的风格写法(更直观)"""
            article_info = {
                "article_detail_url": {'key_value': article_detail_url, 'notes': '文章详情链接'},
                "article_title": {'key_value': article_title, 'notes': '文章标题'},
                "comment_count": {'key_value': comment_count, 'notes': '文章评论数量'},
                "favor_count": {'key_value': favor_count, 'notes': '文章赞成数量'},
                "nick_name": {'key_value': nick_name, 'notes': '文章作者昵称'}
            }

            AritleInfoItem = MongoDataItem(
                # alldata 用于存储 mongo 的 Document 文档所需要的字段映射
                alldata=article_info,
                # table 为 mongo 的存储 Collection 集合的名称
                table=Table_Enum.aritle_list_table.value['value'],
                # mongo_update_rule 为查询数据是否存在的规则
                mongo_update_rule={"article_detail_url": article_detail_url},
            )
            yield AritleInfoItem

            """2. 旧风格的风格写法"""
            item = dict()
            item['article_detail_url'] = article_detail_url
            item['article_title'] = article_title
            item['comment_count'] = comment_count
            item['favor_count'] = favor_count
            item['nick_name'] = nick_name

            item['item_mode'] = 'MongoDB'
            item['table'] = Table_Enum.aritle_list_table.value['value']
            item['mongo_update_rule'] = {"article_detail_url": article_detail_url}
            yield item
