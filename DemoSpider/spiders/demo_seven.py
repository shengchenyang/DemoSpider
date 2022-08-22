import json
from loguru import logger
from scrapy.http import Request, FormRequest
from DemoSpider.common.AboutProj import Operations
from ayugespidertools.AyugeSpider import AyuSpider


"""
####################################################################################################
# collection_website: CSDN - 专业开发者社区
# collection_content: 热榜文章排名 Demo 采集示例 - 不用存储至数据库，只是用来验证中间件功能
# create_time: 2022-08-18
# explain: 只用来测试各种中间件的功能，无关配置全都去除了
# demand_code_prefix = ''
####################################################################################################
"""


class DemoSevenSpider(AyuSpider):
    name = 'demo_seven'
    allowed_domains = ['httpbin.org']
    start_urls = ['http://httpbin.org/']

    # 初始化配置的类型
    settings_type = 'debug'
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            # 随机请求头
            'ayugespidertools.Middlewares.RandomRequestUaMiddleware': 400,

            # 替换 scrapy Request 请求为 requests 的中间件
            'ayugespidertools.Middlewares.RequestByRequestsMiddleware': 401,
        },
    }

    def start_requests(self):
        """
        测试各种请求
        """

        """测试转移到 requests 的请求功能"""
        # 测试 GET 请求示例一
        yield Request(
            url="http://httpbin.org/get?get_args=1",
            callback=self.parse_get_fir,
            # 这里面的 ck 优先级比 cookies 参数中的高
            headers={
                'Cookie': 'headers_cookies_key1=headers_cookie_value1;'
            },
            cookies={
                'cookies_key1': 'cookies_value1',
            },
            meta={
                "meta_data": "这是用来测试 parse_get_fir meta 的功能"
            },
            dont_filter=True
        )

        # 测试 GET 请求示例二
        yield Request(
            url="http://httpbin.org/get",
            callback=self.parse_get_sec,
            headers={
                'Cookie': 'headers_cookies_key1=headers_cookie_value1;'
            },
            cookies={
                'cookies_key1': 'cookies_value1',
            },
            body=json.dumps({"get_body_key1": "get_body_value1"}),
            meta={
                "meta_data": "这是用来测试 parse_get_sec meta 的功能"
            },
            dont_filter=True
        )

        # 测试 POST 请求示例一
        post_data = {"post_key1": "post_value1", "post_key2": "post_value2"}
        yield Request(
            url="http://httpbin.org/post",
            method="POST",
            callback=self.parse_post_fir,
            headers={
                'Cookie': 'headers_cookies_key1=headers_cookie_value1;'
            },
            body=json.dumps(post_data),
            cookies={
                'cookies_key1': 'cookies_value1',
            },
            meta={
                "meta_data": "这是用来测试 parse_post_fir meta 的功能"
            },
            dont_filter=True
        )

        # 测试 POST 请求示例二
        yield FormRequest(
            url="http://httpbin.org/post",
            headers={
                'Cookie': 'headers_cookies_key1=headers_cookie_value1;'
            },
            cookies={
                'cookies_key1': 'cookies_value1',
            },
            formdata=post_data,
            callback=self.parse_post_sec,
            meta={
                "meta_data": "这是用来测试 parse_post_sec meta 的功能"
            },
            dont_filter=True
        )

    def parse_get_fir(self, response):
        meta_data = response.meta.get("meta_data")
        logger.info(f"get meta_data: {meta_data}")
        Operations.parse_response_data(response_data=response.text, mark="GET FIRST")

    def parse_get_sec(self, response):
        meta_data = response.meta.get("meta_data")
        logger.info(f"get meta_data: {meta_data}")
        Operations.parse_response_data(response_data=response.text, mark="GET SEC")

    def parse_post_fir(self, response):
        meta_data = response.meta.get("meta_data")
        logger.info(f"post first meta_data: {meta_data}")
        Operations.parse_response_data(response_data=response.text, mark="POST FIRST")

    def parse_post_sec(self, response):
        meta_data = response.meta.get("meta_data")
        logger.info(f"post second meta_data: {meta_data}")
        Operations.parse_response_data(response_data=response.text, mark="POST SECOND")
