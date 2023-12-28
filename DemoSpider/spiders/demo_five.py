# 纵横中文网小说书库采集 - 异步存入 Mysql (配置根据本地 .conf 取值)
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


class DemoFiveSpider(AyuSpider):
    name = "demo_five"
    allowed_domains = ["book.zongheng.com"]
    start_urls = ["http://book.zongheng.com"]
    custom_settings = {
        "ITEM_PIPELINES": {
            # 激活此项则数据会存储至 Mysql
            "ayugespidertools.pipelines.AyuTwistedMysqlPipeline": 300,
        },
        "DOWNLOADER_MIDDLEWARES": {
            # 随机请求头
            "ayugespidertools.middlewares.RandomRequestUaMiddleware": 400,
        },
        "CONCURRENT_REQUESTS": 64,
        "DOWNLOAD_DELAY": 0.01,
    }

    def start_requests(self):
        """
        get 请求首页，获取项目列表数据
        """
        for page in range(1, 11):
            url = f"https://b.faloo.com/y_0_0_0_0_3_15_{page}.html"
            yield Request(url=url, callback=self.parse_first, dont_filter=True)

    def parse_first(self, response: "ScrapyResponse"):
        _save_table = "demo_five"

        book_info_list = response.xpath('//div[@class="TwoBox02_01"]/div')
        for book_info in book_info_list:
            book_name = book_info.xpath("div[2]//h1/@title").get()
            _book_href = book_info.xpath("div[2]//h1/a/@href").get()
            book_href = response.urljoin(_book_href)
            book_intro = book_info.xpath(
                'div[2]/div[@class="TwoBox02_06"]/a/text()'
            ).get()

            book_info_item = AyuItem(
                book_name=DataItem(book_name, "小说名称"),
                book_href=DataItem(book_href, "小说链接"),
                book_intro=DataItem(book_intro, "小说简介"),
                _table=DataItem(_save_table, "demo5表"),
            )

            self.slog.info(f"BookInfoItem: {book_info_item}")
            yield book_info_item
