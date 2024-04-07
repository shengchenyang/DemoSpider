"""
NOTE:
    - elasticsearch asyncio 存储场景示例
    - 需要安装 ayugespidertools[database]
"""

from typing import Any, Iterable

from ayugespidertools.items import AyuItem, DataItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request

from DemoSpider.common.types import ScrapyResponse

try:
    from elasticsearch_dsl import Keyword, Text
except ImportError:
    # pip install ayugespidertools[database]
    pass


class DemoEsAsyncSpider(AyuSpider):
    name = "demo_es_async"
    allowed_domains = ["faloo.com"]
    start_urls = ["https://b.faloo.com/"]
    custom_settings = {
        "DATABASE_ENGINE_ENABLED": True,
        "ITEM_PIPELINES": {
            "ayugespidertools.pipelines.AyuAsyncESPipeline": 300,
        },
        "DOWNLOADER_MIDDLEWARES": {
            "ayugespidertools.middlewares.RandomRequestUaMiddleware": 400,
        },
    }

    def start_requests(self) -> Iterable[Request]:
        for page in range(1, 21):
            url = f"https://b.faloo.com/y_0_0_0_0_3_15_{page}.html"
            yield Request(
                url=url,
                callback=self.parse_first,
                dont_filter=True,
            )

    def parse_first(self, response: ScrapyResponse) -> Any:
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
                _table=DataItem(_save_table),
            )
            self.slog.info(f"book_info_item: {book_info_item}")
            yield book_info_item
