# 测试快代理独享代理
from typing import Iterable

from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request

from DemoSpider.common.types import ScrapyResponse


class DemoProxyTwoSpider(AyuSpider):
    name = "demo_proxy_two"
    allowed_domains = ["myip.ipip.net"]
    start_urls = ["https://myip.ipip.net/"]
    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            # 独享代理激活
            "ayugespidertools.middlewares.ExclusiveProxyDownloaderMiddleware": 125,
        },
    }

    def start_requests(self) -> Iterable[Request]:
        """
        get 请求首页，获取项目列表数据
        """
        yield Request(url=self.start_urls[0], callback=self.parse_first)

    def parse_first(self, response: ScrapyResponse) -> None:
        print(response.text)
