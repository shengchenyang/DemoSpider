# 测试快代理动态隧道代理
from typing import Iterable

from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request

from DemoSpider.common.types import ScrapyResponse


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

    def start_requests(self) -> Iterable[Request]:
        """
        get 请求首页，获取项目列表数据
        """
        yield Request(
            url=self.start_urls[0], callback=self.parse_first, dont_filter=True
        )

    def parse_first(self, response: ScrapyResponse) -> None:
        print(response.text)
