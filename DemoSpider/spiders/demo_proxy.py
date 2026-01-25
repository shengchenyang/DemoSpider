"""
代理的简单示例，可以设置静态代理，动态代理，session 代理；
当然你可以使用 demo_aiohttp 示例中的方式来配置请求代理；
你也可以自己写代理中间件，根据本库支持的自定义配置解析方式来自己实现复杂的定制代理方法。

运行此示例时，需要在 .conf 中设置好 [proxy] 部分。
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from DemoSpider.common.types import ScrapyResponse


class DemoProxySpider(AyuSpider):
    name = "demo_proxy"
    allowed_domains = ["myip.ipip.net"]
    start_urls = ["https://myip.ipip.net/"]
    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            "ayugespidertools.middlewares.ProxyDownloaderMiddleware": 125,
        },
    }

    async def start(self) -> AsyncIterator[Any]:
        """
        get 请求首页，获取项目列表数据
        """
        yield Request(url=self.start_urls[0], callback=self.parse_first)

    def parse_first(self, response: ScrapyResponse) -> None:
        print(response.text)
