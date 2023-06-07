import pandas
from ayugespidertools.common.utils import ToolsForAyu
from ayugespidertools.items import DataItem, MongoDataItem, MysqlDataItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request
from scrapy.http.response.text import TextResponse

from DemoSpider.items import TableEnum
from DemoSpider.settings import logger

"""
####################################################################################################
# collection_website: csdn.net - 专业开发者社区
# collection_content: 热榜文章排名采集，并推送至 kafka
# create_time: 2023-06-05
# explain:
# demand_code_prefix = ""
####################################################################################################
"""


class DemoKafkaSpider(AyuSpider):
    name = "demo_kafka"
    allowed_domains = ["csdn.net"]
    start_urls = ["http://csdn.net/"]

    # 数据库表的枚举信息
    custom_table_enum = TableEnum
    custom_settings = {
        "ITEM_PIPELINES": {
            "ayugespidertools.pipelines.KafkaPipeline": 301,
        },
    }

    def start_requests(self):
        """
        get 请求首页，获取项目列表数据
        """
        yield Request(
            url="https://blog.csdn.net/phoenix/web/blog/hot-rank?page=0&pageSize=25&type=",
            callback=self.parse_first,
            headers={
                "referer": "https://blog.csdn.net/rank/list",
            },
            cb_kwargs={
                "curr_site": "csdn",
            },
            dont_filter=True,
        )

    def parse_first(self, response: TextResponse, curr_site: str):
        # 日志使用: scrapy 的 self.logger 或本库的 self.slog 或直接使用全局的 logger handle 也行（根据场景自行选择）
        self.slog.info(f"当前采集的站点为: {curr_site}")

        # 你可以自定义解析规则，使用 lxml 还是 response.css response.xpath 等等都可以。
        data_list = ToolsForAyu.extract_with_json(
            json_data=response.json(), query="data"
        )
        for curr_data in data_list:
            article_detail_url = ToolsForAyu.extract_with_json(
                json_data=curr_data, query="articleDetailUrl"
            )

            article_title = ToolsForAyu.extract_with_json(
                json_data=curr_data, query="articleTitle"
            )

            comment_count = ToolsForAyu.extract_with_json(
                json_data=curr_data, query="commentCount"
            )

            favor_count = ToolsForAyu.extract_with_json(
                json_data=curr_data, query="favorCount"
            )

            nick_name = ToolsForAyu.extract_with_json(
                json_data=curr_data, query="nickName"
            )

            ArticleInfoMysqlItem = MysqlDataItem(
                article_detail_url=DataItem(article_detail_url, "文章详情链接"),
                article_title=DataItem(article_title, "文章标题"),
                comment_count=DataItem(comment_count, "文章评论数量"),
                favor_count=DataItem(favor_count, "文章赞成数量"),
                nick_name=DataItem(nick_name, "文章作者昵称"),
                _table=TableEnum.article_list_table.value["value"],
            )
            self.slog.info(f"ArticleInfoMysqlItem: {ArticleInfoMysqlItem}")
            yield ArticleInfoMysqlItem
