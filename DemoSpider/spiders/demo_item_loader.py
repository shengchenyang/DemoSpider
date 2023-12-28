# 用于介绍 scrapy item 的 itemloaders 的功能，提供调用示例
from typing import TYPE_CHECKING, Union

from ayugespidertools.common.utils import ToolsForAyu
from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuSpider
from itemloaders.processors import TakeFirst
from loguru import logger
from scrapy.http import Request
from scrapy.loader import ItemLoader

if TYPE_CHECKING:
    from scrapy.http import Response
    from scrapy.http.response.html import HtmlResponse
    from scrapy.http.response.text import TextResponse
    from scrapy.http.response.xml import XmlResponse

    ScrapyResponse = Union[TextResponse, XmlResponse, HtmlResponse, Response]


class DemoItemLoaderSpider(AyuSpider):
    name = "demo_item_loader"
    allowed_domains = ["zongheng.com"]
    start_urls = ["http://book.zongheng.com"]
    custom_settings = {
        "ITEM_PIPELINES": {
            # 激活此项则数据会存储至 Mysql
            "ayugespidertools.pipelines.AyuFtyMysqlPipeline": 300,
        },
        "DOWNLOADER_MIDDLEWARES": {
            # 随机请求头
            "ayugespidertools.middlewares.RandomRequestUaMiddleware": 400,
        },
    }

    def start_requests(self):
        for page in range(1, 5):
            yield Request(
                url=f"http://book.zongheng.com/store/c0/c0/b0/u0/p{page}/v9/s9/t0/u0/i1/ALL.html",
                callback=self.parse_first,
                cb_kwargs=dict(
                    curr_site="zongheng",
                ),
                dont_filter=True,
            )

    def parse_first(self, response: "ScrapyResponse", curr_site: str):
        logger.info(f"当前采集站点为: {curr_site}")
        book_info_list = ToolsForAyu.extract_with_xpath(
            response=response, query='//div[@class="bookinfo"]', return_selector=True
        )

        for book_info in book_info_list:
            my_item = AyuItem(
                book_name=None,
                book_href=None,
                book_intro=None,
                _table="demo_item_loader",
            )

            book_name = ToolsForAyu.extract_with_xpath(
                response=book_info, query='div[@class="bookname"]/a/text()'
            )

            mine_item = ItemLoader(item=my_item.asitem(), selector=book_info)
            mine_item.default_output_processor = TakeFirst()
            mine_item.add_value("book_name", book_name)
            mine_item.add_css("book_href", "div.bookname > a::attr(href)")
            mine_item.add_xpath("book_intro", 'div[@class="bookintro"]/text()')
            item = mine_item.load_item()
            yield item
