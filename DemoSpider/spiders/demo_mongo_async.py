# async 存入 mongoDB 的示例，以 motor 实现
from typing import TYPE_CHECKING, Union

from ayugespidertools.items import AyuItem, DataItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request

if TYPE_CHECKING:
    from scrapy.http import Response
    from scrapy.http.response.html import HtmlResponse
    from scrapy.http.response.text import TextResponse
    from scrapy.http.response.xml import XmlResponse

    ScrapyResponse = Union[TextResponse, XmlResponse, HtmlResponse, Response]


class DemoMongoAsyncSpider(AyuSpider):
    name = "demo_mongo_async"
    allowed_domains = ["faloo.com"]
    start_urls = ["http://b.faloo.com/"]
    custom_settings = {
        "ITEM_PIPELINES": {
            # 激活此项则数据会存储至 MongoDB
            "ayugespidertools.pipelines.AyuAsyncMongoPipeline": 300,
        },
        "DOWNLOADER_MIDDLEWARES": {
            # 随机请求头
            "ayugespidertools.middlewares.RandomRequestUaMiddleware": 400,
        },
    }

    def start_requests(self):
        """
        get 请求首页，获取项目列表数据
        """
        for page in range(1, 11):
            url = f"https://b.faloo.com/y_0_0_0_0_3_15_{page}.html"
            yield Request(
                url=url,
                callback=self.parse_first,
                cb_kwargs={
                    "page": page,
                },
                dont_filter=True,
            )

    def parse_first(self, response: "ScrapyResponse", page: int):
        self.slog.info(f"当前采集的站点的第 {page} 页")

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
                _table="demo_mongo_async",
                _mongo_update_rule={"book_name": book_name},
            )

            self.slog.info(f"book_info_item: {book_info_item}")
            yield book_info_item
