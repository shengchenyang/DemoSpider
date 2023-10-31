from ayugespidertools.items import AyuItem, DataItem
from ayugespidertools.spiders import AyuCrawlSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

"""
########################################################################################################################
# collection_website: https://www.book.zongheng.com/ - 纵横中文网
# collection_content: 纵横中文网小说书库采集 CrawlSpider 方式示例
# create_time: 2022-09-30
# explain:
# demand_code_prefix = ""
########################################################################################################################
"""


class DemoCrawlSpider(AyuCrawlSpider):
    name = "demo_crawl"
    allowed_domains = ["qidian.com"]
    start_urls = ["https://www.qidian.com/rank/hotsales/"]
    custom_settings = {
        "ITEM_PIPELINES": {
            # 激活此项则数据会存储至 Mysql
            "ayugespidertools.pipelines.AyuFtyMysqlPipeline": 300,
        },
        "DOWNLOADER_MIDDLEWARES": {
            # 随机请求头
            "ayugespidertools.middlewares.RandomRequestUaMiddleware": 400,
        },
    }

    rules = (
        Rule(
            LinkExtractor(restrict_xpaths="//ul/li/div[@class='book-mid-info']/h2/a"),
            callback="parse_item",
        ),
    )

    def parse_item(self, response):
        # 获取图书名称 - （获取的是详情页中的图书名称）
        book_name_list = response.xpath("//h1[@id='bookName']//text()").extract()
        book_name = "".join(book_name_list).strip()

        NovelInfoItem = AyuItem(
            book_name=book_name,
            _table="demo_crawl",
        )
        self.slog.info(f"NovelInfoItem: {NovelInfoItem}")
        yield NovelInfoItem
