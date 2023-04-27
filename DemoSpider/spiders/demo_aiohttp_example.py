import json

from ayugespidertools.common.typevars import AiohttpRequestArgs
from ayugespidertools.request import AiohttpFormRequest, AiohttpRequest
from ayugespidertools.spiders import AyuSpider
from loguru import logger
from scrapy.http.response.text import TextResponse

from DemoSpider.common.AboutProj import Operations

"""
########################################################################################################################
# collection_website: httpbin.org - http://httpbin.org/
# collection_content: 测试将 scrapy Request 改为 aiohttp 的示例
# create_time: 2022-08-30
# explain:
# demand_code_prefix = ""
########################################################################################################################
"""


class DemoAiohttpSpider(AyuSpider):
    name = "demo_aiohttp_example"
    allowed_domains = ["httpbin.org"]
    start_urls = ["http://httpbin.org/"]

    # 初始化配置的类型
    settings_type = "debug"
    custom_settings = {
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "DOWNLOADER_MIDDLEWARES": {
            # 随机请求头
            "ayugespidertools.middlewares.RandomRequestUaMiddleware": 400,
            # 将 scrapy Request 替换为 aiohttp 方式
            "ayugespidertools.middlewares.AiohttpDownloaderMiddleware": 543,
            # 'ayugespidertools.DownloaderMiddlewares.AiohttpAsyncMiddleware': 543,
        },
        # scrapy Request 替换为 aiohttp 的配置示例
        "LOCAL_AIOHTTP_CONFIG": {
            "timeout": 20,
            # "proxy": "http://127.0.0.1:7890",
            "sleep": 0,
            "retry_times": 3,
        },
    }

    def start_requests(self):
        """
        get 请求首页，获取项目列表数据
        """
        # 测试 GET 请求示例一
        yield AiohttpRequest(
            url="http://httpbin.org/get?get_args=1",
            callback=self.parse_get_fir,
            headers={
                "Cookie": "headers_ck_key=ck; headers_ck_key2=ck",
            },
            cookies={
                "ck_key": "ck",
            },
            meta={
                "meta_data": "这是用来测试 parse_get_fir meta 的功能",
            },
            cb_kwargs={
                "request_name": "normal_get",
            },
        )

        yield AiohttpRequest(
            url="http://httpbin.org/get?get_args=1",
            callback=self.parse_get_fir,
            meta={
                "meta_data": "这是用来测试 parse_get_fir meta 的功能",
            },
            cb_kwargs={
                "request_name": "aiohttp_get",
            },
            args=AiohttpRequestArgs(
                method="GET",
                headers={
                    "Cookie": "headers_ck_key=ck; headers_ck_key2=ck",
                },
                cookies={
                    "ck_key": "ck",
                },
            ),
            dont_filter=True,
        )

        # 测试 POST 请求示例一 - normal
        post_data = {"post_key1": "post_value1", "post_key2": "post_value2"}
        yield AiohttpRequest(
            url="http://httpbin.org/post",
            method="POST",
            callback=self.parse_post_fir,
            headers={
                "Cookie": "headers_ck_key=ck; headers_ck_key2=ck",
            },
            body=json.dumps(post_data),
            cookies={
                "ck_key": "ck",
            },
            meta={
                "meta_data": "这是用来测试 parse_post_fir meta 的功能",
            },
            cb_kwargs={
                "request_name": "normal_post1",
            },
            dont_filter=True,
        )
        # 测试 POST 请求示例一 - aiohttp args
        yield AiohttpRequest(
            url="http://httpbin.org/post",
            callback=self.parse_post_fir,
            args=AiohttpRequestArgs(
                method="POST",
                headers={
                    "Cookie": "headers_ck_key=ck; headers_ck_key2=ck",
                },
                cookies={
                    "ck_key": "ck",
                },
                data=json.dumps(post_data),
            ),
            meta={
                "meta_data": "这是用来测试 parse_post_fir meta 的功能",
            },
            cb_kwargs={
                "request_name": "aiohttp_post1",
            },
            dont_filter=True,
        )

        # 测试 POST 请求示例二 - normal
        yield AiohttpFormRequest(
            url="http://httpbin.org/post",
            headers={
                "Cookie": "headers_ck_key=ck; headers_ck_key2=ck",
            },
            cookies={
                "ck_key": "ck",
            },
            formdata=post_data,
            callback=self.parse_post_sec,
            meta={
                "meta_data": "这是用来测试 parse_post_sec meta 的功能",
            },
            cb_kwargs={
                "request_name": "normal_post2",
            },
            dont_filter=True,
        )
        # 测试 POST 请求示例二 - aiohttp args
        yield AiohttpFormRequest(
            url="http://httpbin.org/post",
            callback=self.parse_post_sec,
            args=AiohttpRequestArgs(
                method="POST",
                headers={
                    "Cookie": "headers_ck_key=ck; headers_ck_key2=ck",
                },
                cookies={
                    "ck_key": "ck",
                },
                data=post_data,
            ),
            meta={
                "meta_data": "这是用来测试 parse_post_sec meta 的功能",
            },
            cb_kwargs={
                "request_name": "aiohttp_post2",
            },
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
