# 纵横中文网小说书库采集 - 测试 aiohttp 请求的功能示例
from typing import TYPE_CHECKING, Union

from ayugespidertools.common.typevars import AiohttpRequestArgs
from ayugespidertools.items import AyuItem
from ayugespidertools.request import AiohttpRequest
from ayugespidertools.spiders import AyuSpider

if TYPE_CHECKING:
    from scrapy.http import Response
    from scrapy.http.response.html import HtmlResponse
    from scrapy.http.response.text import TextResponse
    from scrapy.http.response.xml import XmlResponse

    ScrapyResponse = Union[TextResponse, XmlResponse, HtmlResponse, Response]


class DemoAiohttpTestSpider(AyuSpider):
    name = "demo_aiohttp_test"
    allowed_domains = ["book.zongheng.com"]
    start_urls = ["http://book.zongheng.com"]
    custom_settings = {
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "DOWNLOADER_MIDDLEWARES": {
            # 使用 aiohttp 请求的中间件
            "ayugespidertools.middlewares.AiohttpDownloaderMiddleware": 543,
        },
        # scrapy Request 替换为 aiohttp 的配置示例
        "AIOHTTP_CONFIG": {
            "timeout": 5,
            # "proxy": "127.0.0.1:1080",
            "sleep": 0,
            "retry_times": 3,
        },
        "CONCURRENT_REQUESTS": 100,
        "DOWNLOAD_DELAY": 0.01,
    }

    def start_requests(self):
        """
        get 请求首页，获取项目列表数据
        """
        for page in range(1, 20):
            yield AiohttpRequest(
                url=f"http://book.zongheng.com/store/c0/c0/b0/u0/p{page}/v9/s9/t0/u0/i1/ALL.html",
                callback=self.parse_first,
                meta={
                    "meta_data": "这是用来测试 parse_first meta 的功能",
                    "aiohttp_args": {
                        "timeout": 10,
                        "tmp": "tmp_data",
                    },
                },
                args=AiohttpRequestArgs(
                    timeout=35,
                ),
                dont_filter=True,
            )

    def parse_first(self, response: "ScrapyResponse"):
        book_info_list = response.xpath('//div[@class="bookinfo"]')
        for book_info in book_info_list:
            book_name = book_info.xpath('div[@class="bookname"]/a/text()').get()
            book_href = book_info.xpath('div[@class="bookname"]/a/@href').get()
            book_intro = book_info.xpath('div[@class="bookintro"]/text()').get()
            BookInfoItem = AyuItem(
                book_name=book_name,
                book_href=book_href,
                book_intro=book_intro,
                _table="demo_aiohttp_test",
            )
            self.slog.info(f"BookInfoItem: {BookInfoItem}")
