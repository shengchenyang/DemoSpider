from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request

from DemoSpider.settings import EXCLUSIVE_PROXY_CONFIG

"""
########################################################################################################################
# collection_website: myip - myip.ipip.net
# collection_content: 测试快代理独享代理
# create_time: 2022-09-05
# explain:
# demand_code_prefix = ""
########################################################################################################################
"""


class DemoProxyTwoSpider(AyuSpider):
    name = "demo_proxy_two"
    allowed_domains = ["myip.ipip.net"]
    start_urls = ["https://myip.ipip.net/"]

    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            # 独享代理激活
            "ayugespidertools.middlewares.ExclusiveProxyDownloaderMiddleware": 125,
        },
        # 独享代理对应配置(激活 DOWNLOADER_MIDDLEWARES 中的独享代理时使用)。在 settings 中配置了即可，这里有点重复了，只设置以便即可，这里为了方便展示而已。
        "EXCLUSIVE_PROXY_CONFIG": {
            "proxy": EXCLUSIVE_PROXY_CONFIG["proxy"],
            "username": EXCLUSIVE_PROXY_CONFIG["username"],
            "password": EXCLUSIVE_PROXY_CONFIG["password"],
            "index": EXCLUSIVE_PROXY_CONFIG["index"],
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
