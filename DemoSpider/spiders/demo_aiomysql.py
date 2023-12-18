# 此场景不会自动创建数据库，数据表，表字段等，请手动管理
from ayugespidertools.common.utils import ToolsForAyu
from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request

"""
########################################################################################################################
# collection_website: CSDN - 专业开发者社区
# collection_content: 热榜文章排名 aiomysql Demo 采集示例 - 存入 Mysql (配置根据本地 settings 的 LOCAL_MYSQL_CONFIG 中取值)
# create_time: 2023-12-18
# explain:
# demand_code_prefix = 
########################################################################################################################
"""


class DemoAiomysqlSpider(AyuSpider):
    name = "demo_aiomysql"
    allowed_domains = ["*"]
    start_urls = ["https://b.faloo.com/y_0_0_0_0_3_15_1.html"]
    custom_settings = {
        "LOG_LEVEL": "ERROR",
        "ITEM_PIPELINES": {
            # 激活此项则数据会存储至 Mysql，使用 aiomysql 实现
            "ayugespidertools.pipelines.AyuAsyncMysqlPipeline": 300,
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

            _save_table = "demo_aiomysql"
            BookInfoItem = AyuItem(
                book_name=book_name,
                book_href=book_href,
                book_intro=book_intro,
                _table=_save_table,
            )

            # 运行前请自行创建相关库及表
            self.slog.info(f"BookInfoItem: {BookInfoItem}")
            yield BookInfoItem
