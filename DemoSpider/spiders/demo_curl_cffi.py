"""
使用 curl_cffi 库请求的示例：
CurlCffiRequest 的请求参数与 curl_cffi 一致。

当然如果你不想显性地传递和 curl_cffi 一致的参数，你可以选择使用和 https://github.com/jxlil/scrapy-impersonate
那样通过设置 DOWNLOAD_HANDLERS 来保持发送请求统一还是 scrapy.Request 的方式。
具体使用偏好按需选择，都兼容的。
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ayugespidertools.request import CurlCffiRequest
from ayugespidertools.spiders import AyuSpider

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from scrapy.http.response import Response


class DemoCurlCffiSpider(AyuSpider):
    name = "demo_curl_cffi"
    allowed_domains = ["browserleaks.com"]
    start_urls = ["https://tls.browserleaks.com/json"]
    custom_settings = {
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "DOWNLOADER_MIDDLEWARES": {
            # 将 scrapy Request 替换为 curl_cffi 方式
            "ayugespidertools.middlewares.CurlCffiDownloaderMiddleware": 543,
        },
    }

    async def start(self) -> AsyncIterator[Any]:
        for idx in range(5):
            yield CurlCffiRequest(
                url="https://tls.browserleaks.com/json",
                callback=self.parse_first,
                cb_kwargs={"request_idx": idx},
                impersonate="chrome124",
                dont_filter=True,
            )

    async def parse_first(self, response: Response, request_idx: int) -> Any:
        self.slog.info(f"{request_idx} ja3_hash: {response.json()['ja3_hash']}")
