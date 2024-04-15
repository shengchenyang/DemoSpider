# 测试将 scrapy Request 改为 aiohttp 的示例
import json
from typing import Iterable, Union

from ayugespidertools.common.typevars import AiohttpRequestArgs
from ayugespidertools.request import AiohttpFormRequest, AiohttpRequest
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
            # 随机请求头
            "ayugespidertools.middlewares.RandomRequestUaMiddleware": 400,
            # 将 scrapy Request 替换为 aiohttp 方式
            "ayugespidertools.middlewares.AiohttpDownloaderMiddleware": 543,
        },
        # scrapy Request 替换为 aiohttp 的配置示例
        "AIOHTTP_CONFIG": {
            # "proxy": "http://127.0.0.1:7890",
            "sleep": 0,
            # 同时连接的总数
            "limit": 100,
            # 同时连接到一台主机的数量
            "limit_per_host": 30,
            "retry_times": 3,
            "ssl": False,
            # "verify_ssl": False,
            "allow_redirects": False,
        },
        "DOWNLOAD_TIMEOUT": 35,
    }

    def start_requests(self) -> Iterable[Union[AiohttpRequest, AiohttpFormRequest]]:
        # 这里是一些复用的参数，用于请求示例的功能展示
        _get_url = "http://httpbin.org/get?get_args=1"
        _ar_headers_ck = "headers_ck_key=ck; headers_ck_key2=ck"
        _ar_ck = {"ck_key": "ck"}

        """
        NOTE:
            1.以下的示例中的 meta 和 cb_kwargs 参数都不是必须的，里面的配置也不是必须的，这里
        只是给出一个比较完整的示例，请按需配置。

            2.特别是 meta，如果没有自己实现的中间件来使用其中的配置，那么推荐直接删除，开发者需
        要传递的参数更推荐放入 cb_kwargs 中。
        """

        # GET normal 示例
        yield AiohttpRequest(
            url=_get_url,
            callback=self.parse_get_fir,
            headers={"Cookie": _ar_headers_ck},
            cookies=_ar_ck,
            cb_kwargs={"request_name": 1},
        )

        # GET with aiohttp args 示例
        yield AiohttpRequest(
            url=_get_url,
            callback=self.parse_get_fir,
            cb_kwargs={"request_name": 2},
            args=AiohttpRequestArgs(
                method="GET",
                headers={"Cookie": _ar_headers_ck},
                cookies=_ar_ck,
            ),
            dont_filter=True,
        )

        # POST normal 示例
        post_data = {"post_key1": "post_value1", "post_key2": "post_value2"}
        yield AiohttpRequest(
            url="http://httpbin.org/post",
            method="POST",
            callback=self.parse_post_fir,
            headers={"Cookie": _ar_headers_ck},
            body=json.dumps(post_data),
            cookies=_ar_ck,
            cb_kwargs={"request_name": 3},
            dont_filter=True,
        )

        # POST with aiohttp args 示例
        yield AiohttpRequest(
            url="http://httpbin.org/post",
            callback=self.parse_post_fir,
            args=AiohttpRequestArgs(
                method="POST",
                headers={"Cookie": _ar_headers_ck},
                cookies=_ar_ck,
                data=json.dumps(post_data),
            ),
            cb_kwargs={"request_name": 4},
            dont_filter=True,
        )

        # POST(FormRequest) 示例
        yield AiohttpFormRequest(
            url="http://httpbin.org/post",
            headers={"Cookie": _ar_headers_ck},
            cookies=_ar_ck,
            formdata=post_data,
            callback=self.parse_post_sec,
            cb_kwargs={"request_name": 5},
            dont_filter=True,
        )

        # POST(FormRequest) with aiohttp args 示例
        yield AiohttpFormRequest(
            url="http://httpbin.org/post",
            callback=self.parse_post_sec,
            args=AiohttpRequestArgs(
                method="POST",
                headers={"Cookie": _ar_headers_ck},
                cookies=_ar_ck,
                data=post_data,
            ),
            cb_kwargs={"request_name": 6},
            dont_filter=True,
        )

        # 另一种风格示例，以 POST(FormRequest) with aiohttp args 为例：
        # 将 aiohttp 参数放入 meta 的 aiohttp 的 args 中；
        # 但还是推荐 args=AiohttpRequestArgs() 的方式，有参数提示，比较方便。
        yield AiohttpFormRequest(
            url="http://httpbin.org/post",
            callback=self.parse_post_sec,
            meta={
                "aiohttp": {
                    "args": {
                        "method": "POST",
                        "headers": {"Cookie": _ar_headers_ck},
                        "cookies": _ar_ck,
                        "data": post_data,
                    }
                },
            },
            cb_kwargs={"request_name": 7},
            dont_filter=True,
        )

    # 此处及后面所有的 parse_xx_xx 方法都是用于对响应信息的解析，用于测试
    def parse_get_fir(self, response: ScrapyResponse, request_name: int) -> None:
        self.slog.info(f"get & request_name: {request_name}")
        Operations.parse_response_data(response_data=response.text, mark="GET FIRST")

    def parse_post_fir(self, response: ScrapyResponse, request_name: int) -> None:
        self.slog.info(f"post & request_name: {request_name}")
        Operations.parse_response_data(response_data=response.text, mark="POST FIRST")

    def parse_post_sec(self, response: ScrapyResponse, request_name: int) -> None:
        self.slog.info(f"post && request_name {request_name}")
        Operations.parse_response_data(response_data=response.text, mark="POST SECOND")
