# 测试快代理动态隧道代理
from typing import TYPE_CHECKING, Union

from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request

if TYPE_CHECKING:
    from scrapy.http import Response
    from scrapy.http.response.html import HtmlResponse
    from scrapy.http.response.text import TextResponse
    from scrapy.http.response.xml import XmlResponse

    ScrapyResponse = Union[TextResponse, XmlResponse, HtmlResponse, Response]


class DemoProxySpider(AyuSpider):
    name = "demo_proxy_one"
    allowed_domains = ["myip.ipip.net"]
    start_urls = ["https://myip.ipip.net/"]
    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            # 动态隧道代理激活
            "ayugespidertools.middlewares.DynamicProxyDownloaderMiddleware": 125,
        },
    }

    def start_requests(self):
        """
        get 请求首页，获取项目列表数据
        """
        yield Request(
            url=self.start_urls[0], callback=self.parse_first, dont_filter=True
        )

    def parse_first(self, response: "ScrapyResponse"):
        print(response.text)
