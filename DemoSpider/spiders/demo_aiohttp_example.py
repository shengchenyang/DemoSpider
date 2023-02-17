import json

from ayugespidertools.AyugeSpider import AyuSpider
from ayugespidertools.AyuRequest import AioFormRequest, AiohttpRequest
from loguru import logger

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
            "ayugespidertools.Middlewares.RandomRequestUaMiddleware": 400,
            # 将 scrapy Request 替换为 aiohttp 方式
            "ayugespidertools.DownloaderMiddlewares.AiohttpMiddleware": 543,
            # 'ayugespidertools.DownloaderMiddlewares.AiohttpAsyncMiddleware': 543,
        },
        # scrapy Request 替换为 aiohttp 的配置示例
        "LOCAL_AIOHTTP_CONFIG": {
            "TIMEOUT": 5,
            "PROXY": "127.0.0.1:1080",
            "SLEEP": 0,
            "RETRY_TIMES": 3,
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
            # aiohttp 的中间件下，headers 和 cookies 参数中的 ck 值不会冲突，但是当两参数中的 key 值一样时，库中默认取 cookies 中的值。
            # 所以此时，cookies 参数的优先级比较高
            headers={
                "Cookie": "headers_cookies_key1=headers_cookie_value1; test_key=test_headers_value"
            },
            cookies={
                "cookies_key1": "cookies_value1",
                "test_key": "test_cookies_value",
            },
            meta={
                "meta_data": "这是用来测试 parse_get_fir meta 的功能",
                "aiohttp_args": {
                    "timeout": 3,
                    "proxy": "这个功能暂不提供，后续添加",
                },
            },
            dont_filter=True,
        )

        # 测试 POST 请求示例一
        post_data = {"post_key1": "post_value1", "post_key2": "post_value2"}
        yield AiohttpRequest(
            url="http://httpbin.org/post",
            method="POST",
            callback=self.parse_post_fir,
            headers={
                "Cookie": "headers_cookies_key1=headers_cookie_value1; headers_cookies_key2=v2"
            },
            body=json.dumps(post_data),
            # cookies={
            #     'cookies_key1': 'cookies_value1',
            # },
            meta={
                "meta_data": "这是用来测试 parse_post_fir meta 的功能",
                "aiohttp_args": {
                    "timeout": 3,
                    "proxy": "这个功能暂不提供，后续添加",
                },
            },
            dont_filter=True,
        )

        # 测试 POST 请求示例二
        yield AioFormRequest(
            url="http://httpbin.org/post",
            headers={"Cookie": "headers_cookies_key1=headers_cookie_value1;"},
            cookies={
                "cookies_key1": "cookies_value1",
            },
            formdata=post_data,
            callback=self.parse_post_sec,
            meta={
                "meta_data": "这是用来测试 parse_post_sec meta 的功能",
                "aiohttp_args": {
                    "timeout": 3,
                    "proxy": "这个功能暂不提供，后续添加",
                },
            },
            dont_filter=True,
        )

    def parse_get_fir(self, response):
        meta_data = response.meta.get("meta_data")
        logger.info(f"get meta_data: {meta_data}")
        Operations.parse_response_data(response_data=response.text, mark="GET FIRST")

    def parse_post_fir(self, response):
        meta_data = response.meta.get("meta_data")
        logger.info(f"post first meta_data: {meta_data}")
        Operations.parse_response_data(response_data=response.text, mark="POST FIRST")

    def parse_post_sec(self, response):
        meta_data = response.meta.get("meta_data")
        logger.info(f"post second meta_data: {meta_data}")
        Operations.parse_response_data(response_data=response.text, mark="POST SECOND")
