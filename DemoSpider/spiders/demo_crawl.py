from ayugespidertools.items import DataItem, MysqlDataItem
from ayugespidertools.spiders import AyuCrawlSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from DemoSpider.items import TableEnum

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
    allowed_domains = ["zongheng.com"]
    start_urls = ["https://www.zongheng.com/rank/details.html?rt=1&d=1"]

    # 数据库表的枚举信息
    custom_table_enum = TableEnum
    # 初始化配置的类型
    settings_type = "debug"
    custom_settings = {
        "LOG_LEVEL": "DEBUG",
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
            LinkExtractor(restrict_xpaths='//div[@class="rank_d_b_name"]/a'),
            callback="parse_item",
        ),
    )

    def parse_item(self, response):
        # 获取图书名称 - （获取的是详情页中的图书名称）
        book_name_list = response.xpath('//div[@class="book-name"]//text()').extract()
        book_name = "".join(book_name_list).strip()

        NovelInfoItem = MysqlDataItem(
            book_name=book_name,
            _table=TableEnum.article_list_table.value["value"],
        )
        self.slog.info(f"NovelInfoItem: {NovelInfoItem}")
        yield NovelInfoItem
