# 测试 aiohttp 请求的功能示例
from typing import Any, Iterable

from ayugespidertools.items import AyuItem
from ayugespidertools.request import AiohttpRequest
from ayugespidertools.spiders import AyuSpider

from DemoSpider.common.types import ScrapyResponse


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

    def start_requests(self) -> Iterable[AiohttpRequest]:
        """
        get 请求首页，获取项目列表数据
        """
        for page in range(1, 11):
            yield AiohttpRequest(
                url=f"http://book.zongheng.com/store/c0/c0/b0/u0/p{page}/v9/s9/t0/u0/i1/ALL.html",
                callback=self.parse_first,
                dont_filter=True,
            )

    def parse_first(self, response: ScrapyResponse) -> Any:
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
