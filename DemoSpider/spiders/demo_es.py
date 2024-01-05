# demo_es 的方式3实现示例已删除，可通过 commits 历史查看
# 删除的原因是实现方式过于丑陋，会改变为方式2的形式来开发。
# 这里先放上伪代码实现，es 支持会以以下风格开发。

"""
from typing import TYPE_CHECKING, Union

from ayugespidertools.items import AyuItem, DataItem
from ayugespidertools.spiders import AyuSpider
from elasticsearch_dsl import Keyword, Text
from scrapy.http import Request

if TYPE_CHECKING:
    from scrapy.http import Response
    from scrapy.http.response.html import HtmlResponse
    from scrapy.http.response.text import TextResponse
    from scrapy.http.response.xml import XmlResponse

    ScrapyResponse = Union[TextResponse, XmlResponse, HtmlResponse, Response]


class DemoEsSpider(AyuSpider):
    name = "demo_es"
    allowed_domains = ["faloo.com"]
    start_urls = ["https://b.faloo.com/"]
    custom_settings = {
        "ITEM_PIPELINES": {
            "ayugespidertools.pipelines.AyuESPipeline": 300,
        },
        "DOWNLOADER_MIDDLEWARES": {
            "ayugespidertools.middlewares.RandomRequestUaMiddleware": 400,
        },
    }

    def start_requests(self):
        for page in range(1, 2):
            url = f"https://b.faloo.com/y_0_0_0_0_3_15_{page}.html"
            yield Request(
                url=url,
                callback=self.parse_first,
                cb_kwargs={
                    "page": page,
                },
                dont_filter=True,
            )

    def parse_first(self, response: "ScrapyResponse", page: int):
        _save_table = "demo_es"

        book_info_list = response.xpath('//div[@class="TwoBox02_01"]/div')
        for book_info in book_info_list:
            book_name = book_info.xpath("div[2]//h1/@title").get()
            _book_href = book_info.xpath("div[2]//h1/a/@href").get()
            book_href = response.urljoin(_book_href)
            book_intro = book_info.xpath(
                'div[2]/div[@class="TwoBox02_06"]/a/text()'
            ).get()

            book_info_item = AyuItem(
                book_name=DataItem(
                    book_name, Text(analyzer="snowball", fields={"raw": Keyword()})
                ),
                book_href=DataItem(book_href, Keyword()),
                book_intro=DataItem(book_intro, Keyword()),
                _table=DataItem("demo_es"),
            )
            self.slog.info(f"book_info_item: {book_info_item}")
            yield book_info_item
"""
