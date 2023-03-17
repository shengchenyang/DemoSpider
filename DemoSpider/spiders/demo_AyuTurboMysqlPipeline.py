#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from ayugespidertools.AyugeSpider import AyuSpider
from ayugespidertools.common.Utils import ToolsForAyu
from ayugespidertools.Items import DataItem, MysqlDataItem
from scrapy.http import Request
from scrapy.http.response.text import TextResponse

from DemoSpider.common.DataEnum import TableEnum
from DemoSpider.settings import logger

"""
########################################################################################################################
# collection_website: csdn.net - 采集的目标站点介绍
# collection_content: 采集内容介绍，用于介绍使用 mysql 连接池的示例功能
# create_time: xxxx-xx-xx
# explain:
# demand_code_prefix = ""
########################################################################################################################
"""


class DemoAyuturbomysqlpipelineSpider(AyuSpider):
    name = "demo_AyuTurboMysqlPipeline"
    allowed_domains = ["csdn.net"]
    start_urls = ["http://csdn.net/"]

    # 数据库表的枚举信息
    custom_table_enum = TableEnum
    # 初始化配置的类型
    settings_type = "debug"
    custom_settings = {
        # 是否开启记录项目相关运行统计信息
        "RECORD_LOG_TO_MYSQL": False,
        "LOGURU_CONFIG": logger,
        # 数据表的前缀名称，用于标记属于哪个项目，也可以不用添加或配置
        "MYSQL_TABLE_PREFIX": "demo_turbo_",
        "ITEM_PIPELINES": {
            # 激活此项则数据会存储至 Mysql
            "ayugespidertools.Pipelines.AyuTurboMysqlPipeline": 300,
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
        yield Request(
            url="https://blog.csdn.net/phoenix/web/blog/hot-rank?page=0&pageSize=25&type=",
            callback=self.parse_first,
            headers={
                "referer": "https://blog.csdn.net/rank/list",
            },
            cb_kwargs=dict(
                curr_site="csdn",
            ),
            dont_filter=True,
        )

    def parse_first(self, response: TextResponse, curr_site: str):
        logger.info(f"当前采集站点为: {curr_site}")
        data_list = ToolsForAyu.extract_with_json(
            json_data=response.json(), query="data"
        )
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

            article_info = {
                "article_detail_url": DataItem(article_detail_url, "文章详情链接"),
                "article_title": DataItem(article_title, "文章标题"),
                "comment_count": DataItem(comment_count, "文章评论数量"),
                "favor_count": DataItem(favor_count, "文章赞成数量"),
                "nick_name": DataItem(nick_name, "文章作者昵称"),
            }

            # 存储到 mysql 的示例
            ArticleInfoMysqlItem = MysqlDataItem(
                alldata=article_info,
                table=TableEnum.article_list_table.value["value"],
            )

            # 数据入库逻辑 -> 测试 mysql_engine 的去重功能
            sql = """select `id` from `{}` where `article_detail_url` = "{}" limit 1""".format(
                self.custom_settings.get("MYSQL_TABLE_PREFIX", "")
                + TableEnum.article_list_table.value["value"],
                article_detail_url,
            )
            yield ToolsForAyu.filter_data_before_yield(
                sql=sql, mysql_engine=self.mysql_engine, item=ArticleInfoMysqlItem
            )
