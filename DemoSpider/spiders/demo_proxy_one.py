from ayugespidertools.AyugeSpider import AyuSpider
from scrapy.http import Request

from DemoSpider.settings import DYNAMIC_PROXY_CONFIG

"""
########################################################################################################################
# collection_website: myip - myip.ipip.net
# collection_content: 测试快代理动态隧道代理
# create_time: 2022-08-30
# explain:
# demand_code_prefix = ""
########################################################################################################################
"""


class DemoProxySpider(AyuSpider):
    name = "demo_proxy_one"
    allowed_domains = ["myip.ipip.net"]
    start_urls = ["https://myip.ipip.net/"]

    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            # 动态隧道代理激活
            "ayugespidertools.Middlewares.DynamicProxyDownloaderMiddleware": 125,
            "scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware": None,
        },
        # 动态代理对应配置(激活 DOWNLOADER_MIDDLEWARES 中的动态隧道代理时使用)。在 settings 中配置了即可，这里有点重复了，只设置一遍即可，这里为了方便展示而已。
        "DYNAMIC_PROXY_CONFIG": {
            # 隧道代理服务器域名:端口号（示例: o668.kdltps.com:15818）
            "PROXY_URL": DYNAMIC_PROXY_CONFIG["PROXY_URL"],
            # 用户名 username（隧道代理 tid）
            "USERNAME": DYNAMIC_PROXY_CONFIG["USERNAME"],
            # 对应密码
            "PASSWORD": DYNAMIC_PROXY_CONFIG["PASSWORD"],
        },
    }

    def start_requests(self):
        """
        get 请求首页，获取项目列表数据
        """
        yield Request(
            url=self.start_urls[0], callback=self.parse_first, dont_filter=True
        )

    def parse_first(self, response):
        print(response.text)
