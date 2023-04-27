#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from ayugespidertools.common.utils import ToolsForAyu
from ayugespidertools.items import DataItem, MysqlDataItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request
from scrapy.http.response.text import TextResponse

from DemoSpider.items import TableEnum
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
    custom_settings = {
        # 是否开启记录项目相关运行统计信息
        "RECORD_LOG_TO_MYSQL": False,
        "LOGURU_CONFIG": logger,
        # 数据表的前缀名称，用于标记属于哪个项目，也可以不用添加或配置
        "MYSQL_TABLE_PREFIX": "demo_turbo_",
        "ITEM_PIPELINES": {
            # 激活此项则数据会存储至 Mysql
            "ayugespidertools.pipelines.AyuTurboMysqlPipeline": 300,
        },
        "DOWNLOADER_MIDDLEWARES": {
            # 随机请求头
            "ayugespidertools.middlewares.RandomRequestUaMiddleware": 400,
        },
    }

    # 打开 mysql 引擎开关，用于数据入库前更新逻辑判断
    mysql_engine_enabled = True

    def start_requests(self):
        """
        get 请求首页，获取项目列表数据
        """
        for page in range(1, 11):
            url = f"https://b.faloo.com/y_0_0_0_0_3_15_{page}.html"
            yield Request(
                url=url,
                callback=self.parse_first,
                cb_kwargs=dict(
                    curr_site="zongheng",
                ),
                dont_filter=True,
            )

    def parse_first(self, response: TextResponse, curr_site: str):
        logger.info(f"当前采集站点为: {curr_site}")
        book_info_list = ToolsForAyu.extract_with_xpath(
            response=response,
            query='//div[@class="TwoBox02_01"]/div',
            return_selector=True,
        )

        for book_info in book_info_list:
            book_name = ToolsForAyu.extract_with_xpath(
                response=book_info, query="div[2]//h1/@title"
            )

            book_href = ToolsForAyu.extract_with_xpath(
                response=book_info, query="div[2]//h1/a/@href"
            )
            book_href = response.urljoin(book_href)

            book_intro = ToolsForAyu.extract_with_xpath(
                response=book_info, query='div[2]/div[@class="TwoBox02_06"]/a/text()'
            )

            book_info = {
                "book_name": DataItem(book_name, "小说名称"),
                "book_href": DataItem(book_href, "小说链接"),
                "book_intro": DataItem(book_intro, "小说简介"),
            }

            BookInfoItem = MysqlDataItem(
                alldata=book_info,
                table=TableEnum.book_info_list_table.value["value"],
            )

            # self.slog.info(f"BookInfoItem: {BookInfoItem}")
            yield BookInfoItem
