# 纵横中文网小说书库采集 CrawlSpider 方式示例
from typing import TYPE_CHECKING, Union

from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuCrawlSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule

if TYPE_CHECKING:
    from scrapy.http import Response
    from scrapy.http.response.html import HtmlResponse
    from scrapy.http.response.text import TextResponse
    from scrapy.http.response.xml import XmlResponse

    ScrapyResponse = Union[TextResponse, XmlResponse, HtmlResponse, Response]


class DemoCrawlSpider(AyuCrawlSpider):
    name = "demo_crawl"
    allowed_domains = ["iana.org"]
    start_urls = ["https://www.iana.org/about"]
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

    rules = (
        Rule(
            LinkExtractor(restrict_xpaths="//article/main/ul/li/p/a"),
            callback="parse_item",
        ),
    )

    def parse_item(self, response: "ScrapyResponse"):
        iana_item = AyuItem(
            url=response.url,
            _table="demo_crawl",
        )
        self.slog.info(f"iana_item: {iana_item}")
        yield iana_item
