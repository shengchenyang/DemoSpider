#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from dataclasses import dataclass, field, make_dataclass
from typing import Optional

import pandas
import scrapy
from ayugespidertools.AyugeSpider import AyuSpider
from ayugespidertools.common.Utils import ToolsForAyu
from itemloaders.processors import Join, MapCompose, TakeFirst
from loguru import logger
from scrapy.http import Request
from scrapy.http.response.text import TextResponse
from scrapy.loader import ItemLoader

from DemoSpider.common.DataEnum import TableEnum

"""
########################################################################################################################
# collection_website: csdn.net - 采集的目标站点介绍
# collection_content: 采集内容介绍
# create_time: xxxx-xx-xx
# explain:
# demand_code_prefix = ""
########################################################################################################################
"""


class DemoItemLoaderTwoSpider(AyuSpider):
    name = "demo_item_loader_two"
    allowed_domains = ["zongheng.com"]
    start_urls = ["http://book.zongheng.com"]

    # 数据库表的枚举信息
    custom_table_enum = TableEnum
    # 初始化配置的类型
    settings_type = "debug"
    custom_settings = {
        "ITEM_PIPELINES": {
            # 激活此项则数据会存储至 Mysql
            "ayugespidertools.Pipelines.AyuFtyMysqlPipeline": 300,
        },
        "DOWNLOADER_MIDDLEWARES": {
            # 随机请求头
            "ayugespidertools.Middlewares.RandomRequestUaMiddleware": 400,
        },
    }

    # 打开 mysql 引擎开关，用于数据入库前更新逻辑判断
    mysql_engine_enabled = True

    def start_requests(self):
        page = 1
        yield Request(
            url=f"http://book.zongheng.com/store/c0/c0/b0/u0/p{page}/v9/s9/t0/u0/i1/ALL.html",
            callback=self.parse_first,
            cb_kwargs=dict(
                curr_site="zongheng",
            ),
            dont_filter=True,
        )

    def parse_first(self, response: TextResponse, curr_site: str):
        logger.info(f"当前采集站点为: {curr_site}")
        book_info_list = ToolsForAyu.extract_with_xpath(
            response=response, query='//div[@class="bookinfo"]', return_selector=True
        )

        for book_info in book_info_list:
            book_name = ToolsForAyu.extract_with_xpath(
                response=book_info, query='div[@class="bookname"]/a/text()'
            )

            book_href = ToolsForAyu.extract_with_xpath(
                response=book_info, query='div[@class="bookname"]/a/@href'
            )

            # 可以自行解析出字段，也可以使用下方的 add_xpath("book_intro", xpath_info) 方法
            book_intro = ToolsForAyu.extract_with_xpath(
                response=book_info, query='div[@class="bookintro"]/text()'
            )

            save_table = (
                self.custom_settings.get("MYSQL_TABLE_PREFIX", "")
                + TableEnum.article_list_table.value["value"]
            )
            MineItem = make_dataclass(
                "MineItem",
                [
                    ("book_name", str, field(default=None)),
                    ("book_href", str, field(default=None)),
                    ("book_intro", str, field(default=None)),
                    ("item_mode", str, field(default="Mysql")),
                    ("table", str, field(default=save_table)),
                ],
            )

            mine_item = ItemLoader(item=MineItem(), selector=book_info)
            mine_item.default_output_processor = TakeFirst()
            mine_item.add_value("book_name", book_name)
            mine_item.add_value("book_href", book_href)
            mine_item.add_xpath("book_intro", 'div[@class="bookintro"]/text()')
            item = mine_item.load_item()
            yield item
