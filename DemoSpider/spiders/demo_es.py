# elasticsearch 同步存储场景
# 需要安装 ayugespidertools[database]
from typing import TYPE_CHECKING, Union

from ayugespidertools.items import AyuItem, DataItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request

try:
    from elasticsearch_dsl import Keyword, Search, Text
except ImportError:
    # pip install ayugespidertools[database]
    pass

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
        "DATABASE_ENGINE_ENABLED": True,
        "ITEM_PIPELINES": {
            "ayugespidertools.pipelines.AyuFtyESPipeline": 300,
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
                _table=DataItem(_save_table),
            )

            # 查重逻辑自己设置，精确匹配还是全文搜索请自行设置，这里只是一种示例。
            # 其它的查重和更新方式，比如使用查询并更新的语句。
            s = (
                Search(using=self.es_engine, index=_save_table)
                .query("term", book_href=book_href)
                .execute()
            )
            if s.hits.total.value > 0:
                self.slog.debug(f'链接为 "{book_href}" 的数据已存在')
            else:
                yield book_info_item
