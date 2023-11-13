# 测试将 scrapy Request 改为 aiohttp 的示例
import json

from ayugespidertools.common.typevars import AiohttpRequestArgs
from ayugespidertools.request import AiohttpFormRequest, AiohttpRequest
from ayugespidertools.spiders import AyuSpider
from loguru import logger
from scrapy.http.response.text import TextResponse

from DemoSpider.common.AboutProj import Operations


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
            "limit_per_host": 0,
            "retry_times": 3,
            "verify_ssl": False,
            "allow_redirects": False,
        },
        "DOWNLOAD_TIMEOUT": 35,
    }

    def start_requests(self):
        _get_url = "http://httpbin.org/get?get_args=1"
        _ar_headers_ck = "headers_ck_key=ck; headers_ck_key2=ck"
        _ar_ck = {"ck_key": "ck"}

        # GET normal 示例
        yield AiohttpRequest(
            url=_get_url,
            callback=self.parse_get_fir,
            headers={"Cookie": _ar_headers_ck},
            cookies=_ar_ck,
            meta={"meta_data": "get_normal"},
            cb_kwargs={"request_name": 1},
        )

        # GET with aiohttp args 示例
        yield AiohttpRequest(
            url=_get_url,
            callback=self.parse_get_fir,
            meta={"meta_data": "get_with_aiohttp_args"},
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
            meta={"meta_data": "post_normal"},
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
            meta={"meta_data": "post_with_aiohttp_args"},
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
            meta={"meta_data": "POST(FormRequest)"},
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
            meta={"meta_data": "POST(FormRequest)_with_aiohttp_args"},
            cb_kwargs={"request_name": 6},
            dont_filter=True,
        )

    def parse_get_fir(self, response: TextResponse, request_name: str):
        meta_data = response.meta.get("meta_data")
        logger.info(f"get {request_name} meta_data: {meta_data}")
        Operations.parse_response_data(response_data=response.text, mark="GET FIRST")

    def parse_post_fir(self, response: TextResponse, request_name: str):
        meta_data = response.meta.get("meta_data")
        logger.info(f"post {request_name} first meta_data: {meta_data}")
        Operations.parse_response_data(response_data=response.text, mark="POST FIRST")

    def parse_post_sec(self, response: TextResponse, request_name: str):
        meta_data = response.meta.get("meta_data")
        logger.info(f"post {request_name} second meta_data: {meta_data}")
        Operations.parse_response_data(response_data=response.text, mark="POST SECOND")
