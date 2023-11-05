# async 存入 mongoDB 的示例，以 motor 实现
from ayugespidertools.common.utils import ToolsForAyu
from ayugespidertools.items import AyuItem, DataItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request
from scrapy.http.response.text import TextResponse


class DemoMongoAsyncSpider(AyuSpider):
    name = "demo_mongo_async"
    allowed_domains = ["faloo.com"]
    start_urls = ["http://b.faloo.com/"]
    custom_settings = {
        "ITEM_PIPELINES": {
            # 激活此项则数据会存储至 MongoDB
            "ayugespidertools.pipelines.AsyncMongoPipeline": 300,
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

    def parse_first(self, response: TextResponse, page: int):
        self.slog.info(f"当前采集的站点的第 {page} 页")

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

            BookInfoItem = AyuItem(
                book_name=book_name,
                book_href=book_href,
                book_intro=book_intro,
                _table="demo_mongo_async",
                _mongo_update_rule={"book_name": book_name},
            )
            yield BookInfoItem
