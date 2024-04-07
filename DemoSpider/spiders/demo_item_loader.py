# 用于介绍 scrapy item 的 itemloaders 的功能，提供调用示例
from typing import Any, Iterable

from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuSpider
from itemloaders.processors import TakeFirst
from scrapy.http import Request
from scrapy.loader import ItemLoader

from DemoSpider.common.types import ScrapyResponse


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

    def start_requests(self) -> Iterable[Request]:
        for page in range(1, 5):
            yield Request(
                url=f"http://book.zongheng.com/store/c0/c0/b0/u0/p{page}/v9/s9/t0/u0/i1/ALL.html",
                callback=self.parse_first,
                dont_filter=True,
            )

    def parse_first(self, response: ScrapyResponse) -> Any:
        book_info_list = response.xpath('//div[@class="bookinfo"]')
        for book_info in book_info_list:
            my_item = AyuItem(
                book_name=None,
                book_href=None,
                book_intro=None,
                _table="demo_item_loader",
            )

            book_name = book_info.xpath('div[@class="bookname"]/a/text()').get()

            mine_item = ItemLoader(item=my_item.asitem(), selector=book_info)
            mine_item.default_output_processor = TakeFirst()
            mine_item.add_value("book_name", book_name)
            mine_item.add_css("book_href", "div.bookname > a::attr(href)")
            mine_item.add_xpath("book_intro", 'div[@class="bookintro"]/text()')
            item = mine_item.load_item()
            self.slog.info(f"{item=}")
            yield item
