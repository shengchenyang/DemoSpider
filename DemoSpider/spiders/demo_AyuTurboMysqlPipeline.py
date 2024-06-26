"""
NOTE:
    - 用于介绍使用 mysql 连接池的示例功能；
    - 只用于提供另一种示例，更推荐使用 twisted 或 async 的 pipline 方式。
"""

from typing import Any, Iterable

from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request

from DemoSpider.common.types import ScrapyResponse


class DemoAyuturbomysqlpipelineSpider(AyuSpider):
    name = "demo_AyuTurboMysqlPipeline"
    allowed_domains = ["csdn.net"]
    start_urls = ["http://csdn.net/"]
    custom_settings = {
        "ITEM_PIPELINES": {
            "ayugespidertools.pipelines.AyuTurboMysqlPipeline": 300,
        },
    }

    def start_requests(self) -> Iterable[Request]:
        """
        get 请求首页，获取项目列表数据
        """
        for page in range(1, 11):
            url = f"https://b.faloo.com/y_0_0_0_0_3_15_{page}.html"
            yield Request(
                url=url,
                callback=self.parse_first,
                dont_filter=True,
            )

    def parse_first(self, response: ScrapyResponse) -> Any:
        book_info_list = response.xpath('//div[@class="TwoBox02_01"]/div')
        for book_info in book_info_list:
            book_name = book_info.xpath("div[2]//h1/@title").get()
            _book_href = book_info.xpath("div[2]//h1/a/@href").get()
            book_href = response.urljoin(_book_href)
            book_intro = book_info.xpath(
                'div[2]/div[@class="TwoBox02_06"]/a/text()'
            ).get()

            book_info_item = AyuItem(
                book_name=book_name,
                book_href=book_href,
                book_intro=book_intro,
                _table="demo_AyuTurboMysql",
            )

            self.slog.info(f"book_info_item: {book_info_item}")
            yield book_info_item
