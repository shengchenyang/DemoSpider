# 测试将 scrapy Request 改为 aiohttp 的示例
from typing import Iterable

from ayugespidertools.request import AiohttpRequest
from ayugespidertools.spiders import AyuSpider

from DemoSpider.common.types import ScrapyResponse
from DemoSpider.common.utils import Operations


class DemoAiohttpSpider(AyuSpider):
    name = "demo_aiohttp_example"
    allowed_domains = ["httpbin.org"]
    start_urls = ["http://httpbin.org/"]
    custom_settings = {
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "DOWNLOADER_MIDDLEWARES": {
            # 将 scrapy Request 替换为 aiohttp 方式
            "ayugespidertools.middlewares.AiohttpDownloaderMiddleware": 543,
        },
        # scrapy Request 替换为 aiohttp 的配置示例
        "AIOHTTP_CONFIG": {
            "sleep": 0,
            # 同时连接的总数
            "limit": 100,
            # 同时连接到一台主机的数量
            "limit_per_host": 30,
            "retry_times": 3,
        },
        "DOWNLOAD_TIMEOUT": 35,
    }

    def start_requests(self) -> Iterable[AiohttpRequest]:
        # 这里是一些复用的参数，用于请求示例的功能展示
        _get_url = "http://httpbin.org/get?get_args=1"
        _ar_headers_ck = "headers_ck_key=ck; headers_ck_key2=ck"
        _ar_ck = {"ck_key": "ck"}

        """
        NOTE:
            1.以下的示例中的 cb_kwargs 参数不是必须的，里面的配置也不是必须的，这里只是给出一个比较完
            整的示例，请按需配置。

            2.其中 AiohttpRequest 中的 params，json，data，proxy，ssl，timeout 等参数可按需求自
            定义设置。
        """

        # GET normal 示例
        yield AiohttpRequest(
            url=_get_url,
            callback=self.parse_get_fir,
            headers={"Cookie": _ar_headers_ck},
            cookies=_ar_ck,
            cb_kwargs={"request_name": 1},
        )

        # POST 示例 1
        post_data = {"post_key1": "post_value1", "post_key2": "post_value2"}
        yield AiohttpRequest(
            url="http://httpbin.org/post",
            method="POST",
            callback=self.parse_post,
            headers={"Cookie": _ar_headers_ck},
            data=post_data,
            cookies=_ar_ck,
            cb_kwargs={"request_name": 2},
            dont_filter=True,
        )

        # POST 示例 2
        yield AiohttpRequest(
            url="http://httpbin.org/post",
            method="POST",
            callback=self.parse_post,
            headers={"Cookie": _ar_headers_ck},
            json=post_data,
            cookies=_ar_ck,
            cb_kwargs={"request_name": 3},
            dont_filter=True,
        )

    # 此处及后面所有的 parse_xx_xx 方法都是用于对响应信息的解析，用于测试
    def parse_get_fir(self, response: ScrapyResponse, request_name: int) -> None:
        self.slog.info(f"get & request_name: {request_name}")
        Operations.parse_response_data(response_data=response.text, mark="GET_DEMO")

    def parse_post(self, response: ScrapyResponse, request_name: int) -> None:
        self.slog.info(f"post & request_name: {request_name}")
        Operations.parse_response_data(response_data=response.text, mark="POST_DEMO")
