# 热榜文章排名采集，并推送至 kafka
import json
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


class DemoKafkaSpider(AyuSpider):
    name = "demo_kafka"
    allowed_domains = ["csdn.net"]
    start_urls = ["http://csdn.net/"]
    custom_settings = {
        "ITEM_PIPELINES": {
            "ayugespidertools.pipelines.AyuKafkaPipeline": 301,
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

    def parse_first(self, response: "ScrapyResponse", curr_site: str):
        self.slog.info(f"当前采集的站点为: {curr_site}")

        data_list = json.loads(response.text)["data"]
        for curr_data in data_list:
            article_detail_url = curr_data.get("articleDetailUrl")
            article_title = curr_data.get("articleTitle")
            comment_count = curr_data.get("commentCount")
            favor_count = curr_data.get("favorCount")
            nick_name = curr_data.get("nickName")

            article_item = AyuItem(
                article_detail_url=DataItem(article_detail_url, "文章详情链接"),
                article_title=DataItem(article_title, "文章标题"),
                comment_count=DataItem(comment_count, "文章评论数量"),
                favor_count=DataItem(favor_count, "文章赞成数量"),
                nick_name=DataItem(nick_name, "文章作者昵称"),
                _table=DataItem("demo_kafka", "demo_kafka表"),
            )
            self.slog.info(f"article_item: {article_item}")
            yield article_item
