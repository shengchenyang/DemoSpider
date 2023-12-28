# postgresql asyncio 场景不会添加自动创建数据库，表及字段等功能，请手动管理
from ayugespidertools.common.utils import ToolsForAyu
from ayugespidertools.items import AyuItem, DataItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request
from scrapy.http.response.text import TextResponse


class DemoElevenSpider(AyuSpider):
    name = "demo_eleven"
    allowed_domains = ["faloo.com"]
    start_urls = ["http://b.faloo.com/"]
    custom_settings = {
        "DATABASE_ENGINE_ENABLED": True,
        "ITEM_PIPELINES": {
            "ayugespidertools.pipelines.AyuAsyncPostgresPipeline": 300,
        },
    }

    def start_requests(self):
        for page in range(1, 11):
            url = f"https://b.faloo.com/y_0_0_0_0_3_15_{page}.html"
            yield Request(url=url, callback=self.parse_first, dont_filter=True)

    def parse_first(self, response: TextResponse):
        # 可自定义解析规则
        book_info_list = ToolsForAyu.extract_with_xpath(
            response=response,
            query='//div[@class="TwoBox02_01"]/div',
            return_selector=True,
        )

        for book_info in book_info_list:
            book_name = ToolsForAyu.extract_with_xpath(
                response=book_info, query="div[2]//h1/@title"
            )

            book_href = ToolsForAyu.extract_with_xpath(
                response=book_info, query="div[2]//h1/a/@href"
            )
            book_href = response.urljoin(book_href)

            book_intro = ToolsForAyu.extract_with_xpath(
                response=book_info, query='div[2]/div[@class="TwoBox02_06"]/a/text()'
            )

            _save_table = "demo_eleven"
            BookInfoItem = AyuItem(
                book_name=DataItem(book_name, "小说名称"),
                book_href=DataItem(book_href, "小说链接"),
                book_intro=DataItem(book_intro, "小说简介"),
                _table=DataItem(_save_table, "demo5表"),
            )

            self.slog.info(f"BookInfoItem: {BookInfoItem}")
            yield BookInfoItem