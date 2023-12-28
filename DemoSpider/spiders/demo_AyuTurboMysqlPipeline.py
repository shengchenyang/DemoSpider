# 用于介绍使用 mysql 连接池的示例功能
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


class DemoAyuturbomysqlpipelineSpider(AyuSpider):
    name = "demo_AyuTurboMysqlPipeline"
    allowed_domains = ["csdn.net"]
    start_urls = ["http://csdn.net/"]
    custom_settings = {
        "ITEM_PIPELINES": {
            "ayugespidertools.pipelines.AyuTurboMysqlPipeline": 300,
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
                cb_kwargs=dict(
                    curr_site="zongheng",
                ),
                dont_filter=True,
            )

    def parse_first(self, response: "ScrapyResponse", curr_site: str):
        self.slog.info(f"当前采集站点为: {curr_site}")
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
                _table=DataItem("demo_AyuTurboMysql", "demo_AyuTurboMysql表"),
            )

            self.slog.info(f"book_info_item: {book_info_item}")
            yield book_info_item
