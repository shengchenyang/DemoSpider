from ayugespidertools.common.utils import ToolsForAyu
from ayugespidertools.items import DataItem, MongoDataItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request

from DemoSpider.items import TableEnum

"""
########################################################################################################################
# collection_website: http://book.zongheng.com/ - 纵横中文网
# collection_content: 纵横中文网小说书库采集 - 异步存入 MongoDB (配置根据本地 settings 的 LOCAL_MYSQL_CONFIG 中取值)
# create_time: 2022-08-17
# explain:
# demand_code_prefix = ""
########################################################################################################################
"""


class DemoSixSpider(AyuSpider):
    name = "demo_six"
    allowed_domains = ["book.zongheng.com"]
    start_urls = ["http://book.zongheng.com"]
    custom_settings = {
        "LOG_LEVEL": "ERROR",
        "MONGODB_COLLECTION_PREFIX": "demo6_",
        "ITEM_PIPELINES": {
            # 激活此项则数据会存储至 MongoDB
            "ayugespidertools.pipelines.AyuTwistedMongoPipeline": 300,
        },
        "DOWNLOADER_MIDDLEWARES": {
            # 随机请求头
            "ayugespidertools.middlewares.RandomRequestUaMiddleware": 400,
        },
        "CONCURRENT_REQUESTS": 64,
        "DOWNLOAD_DELAY": 0.1,
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

    def parse_first(self, response, page):
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

            book_info = {
                "book_name": DataItem(book_name, "小说名称"),
                "book_href": DataItem(book_href, "小说链接"),
                "book_intro": DataItem(book_intro, "小说简介"),
            }

            BookInfoItem = MongoDataItem(
                # alldata 用于存储 mongo 的 Document 文档所需要的字段映射
                alldata=book_info,
                # table 为 mongo 的存储 Collection 集合的名称
                table=TableEnum.book_info_list_table.value["value"],
                # mongo_update_rule 为查询数据是否存在的规则
                mongo_update_rule={"book_name": book_name},
            )

            self.slog.info(f"BookInfoItem: {BookInfoItem}")
            yield BookInfoItem
