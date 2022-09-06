import asyncio
import json

import scrapy
from ayugespidertools.AyugeSpider import AyuSpider
from ayugespidertools.common.Utils import ToolsForAyu
from ayugespidertools.Items import MysqlDataItem
from scrapy.http import Request

from DemoSpider.common.DataEnum import TableEnum

"""
########################################################################################################################
# collection_website: CSDN - 专业开发者社区
# collection_content: 热榜文章排名 aiomysql Demo 采集示例 - 存入 Mysql (配置根据本地 settings 的 LOCAL_MYSQL_CONFIG 中取值)
# create_time: 2022-11-09
# explain:
# demand_code_prefix = 
########################################################################################################################
"""


class DemoAiomysqlSpider(AyuSpider):
    name = "demo_aiomysql"
    allowed_domains = ["blog.csdn.net"]
    start_urls = ["https://blog.csdn.net/"]

    # 数据库表的枚举信息
    custom_table_enum = TableEnum
    # 初始化配置的类型
    settings_type = "debug"
    custom_settings = {
        "LOG_LEVEL": "ERROR",
        # 数据表的前缀名称，用于标记属于哪个项目（也可不配置此参数，按需配置）
        "MYSQL_TABLE_PREFIX": "demo_aiomysql_",
        "ITEM_PIPELINES": {
            # 激活此项则数据会存储至 Mysql，使用 aiomysql 实现
            "ayugespidertools.Pipelines.AsyncMysqlPipeline": 300,
        },
        "DOWNLOADER_MIDDLEWARES": {
            # 随机请求头
            "ayugespidertools.Middlewares.RandomRequestUaMiddleware": 400,
        },
    }

    # 打开 mysql 引擎开关，用于数据入库前更新逻辑判断
    mysql_engine_enabled = True

    def start_requests(self):
        """
        get 请求首页，获取项目列表数据
        """
        for page in range(20):
            yield Request(
                url=f"https://blog.csdn.net/phoenix/web/blog/hot-rank?page={page}&pageSize=25&type=",
                callback=self.parse_first,
                headers={
                    "referer": "https://blog.csdn.net/rank/list",
                },
                dont_filter=True,
            )

    def parse_first(self, response):
        data_list = json.loads(response.text)["data"]
        for curr_data in data_list:
            article_detail_url = ToolsForAyu.extract_with_json(
                json_data=curr_data, query="articleDetailUrl"
            )
            article_title = ToolsForAyu.extract_with_json(
                json_data=curr_data, query="articleTitle"
            )
            comment_count = ToolsForAyu.extract_with_json(
                json_data=curr_data, query="commentCount"
            )
            favor_count = ToolsForAyu.extract_with_json(
                json_data=curr_data, query="favorCount"
            )
            nick_name = ToolsForAyu.extract_with_json(
                json_data=curr_data, query="nickName"
            )

            # 数据存储方式1，非常推荐此写法。article_info 含有所有需要存储至表中的字段
            article_info = {
                "article_detail_url": {
                    "key_value": article_detail_url,
                    "notes": "文章详情链接",
                },
                "article_title": {"key_value": article_title, "notes": "文章标题"},
                "comment_count": {"key_value": comment_count, "notes": "文章评论数量"},
                "favor_count": {"key_value": favor_count, "notes": "文章赞成数量"},
                "nick_name": {"key_value": nick_name, "notes": "文章作者昵称"},
            }

            ArticleInfoItem = MysqlDataItem(
                alldata=article_info,
                table=TableEnum.article_list_table.value["value"],
            )

            yield ArticleInfoItem
