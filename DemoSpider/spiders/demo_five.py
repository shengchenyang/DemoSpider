from ayugespidertools.common.utils import ToolsForAyu
from ayugespidertools.items import DataItem, MysqlDataItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request

from DemoSpider.items import TableEnum

"""
########################################################################################################################
# collection_website: http://book.zongheng.com/ - 纵横中文网
# collection_content: 纵横中文网小说书库采集 - 异步存入 Mysql (配置根据本地 settings 的 LOCAL_MYSQL_CONFIG 中取值)
# create_time: 2022-07-30
# explain:
# demand_code_prefix = ""
########################################################################################################################
"""


class DemoFiveSpider(AyuSpider):
    name = "demo_five"
    allowed_domains = ["book.zongheng.com"]
    start_urls = ["http://book.zongheng.com"]

    # 数据库表的枚举信息
    custom_table_enum = TableEnum
    custom_settings = {
        "LOG_LEVEL": "ERROR",
        # 数据表的前缀名称，用于标记属于哪个项目
        "MYSQL_TABLE_PREFIX": "demo5_",
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

    # 打开 mysql 引擎开关，用于数据入库前更新逻辑判断
    mysql_engine_enabled = True

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

            BookInfoItem = MysqlDataItem(
                book_name=DataItem(book_name, "小说名称"),
                book_href=DataItem(book_href, "小说链接"),
                book_intro=DataItem(book_intro, "小说简介"),
                _table=TableEnum.book_info_list_table.value["value"],
            )

            # self.slog.info(f"BookInfoItem: {BookInfoItem}")
            yield BookInfoItem
