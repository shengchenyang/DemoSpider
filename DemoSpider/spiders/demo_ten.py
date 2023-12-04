from ayugespidertools.common.utils import ToolsForAyu
from ayugespidertools.items import AyuItem, DataItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request


class DemoTenSpider(AyuSpider):
    name = "demo_ten"
    allowed_domains = ["book.zongheng.com"]
    start_urls = ["http://book.zongheng.com"]
    custom_settings = {
        "DATABASE_ENGINE_ENABLED": True,
        "ITEM_PIPELINES": {
            "ayugespidertools.pipelines.AyuTwistedPostgresPipeline": 300,
        },
        "DOWNLOADER_MIDDLEWARES": {
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

    def parse_first(self, response):
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

            _save_table = "demo_ten"
            BookInfoItem = AyuItem(
                book_name=DataItem(book_name, "小说名称"),
                book_href=DataItem(book_href, "小说链接"),
                book_intro=DataItem(book_intro, "小说简介"),
                _table=DataItem(_save_table, "demo5表"),
            )

            self.slog.info(f"BookInfoItem: {BookInfoItem}")
            yield BookInfoItem
