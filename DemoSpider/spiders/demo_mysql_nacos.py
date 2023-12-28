# 存储至 mysql 场景，配置从 nacos 获取
import configparser
from typing import TYPE_CHECKING, Union

from ayugespidertools.common.utils import ToolsForAyu
from ayugespidertools.items import AyuItem, DataItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request

from DemoSpider.settings import VIT_DIR

if TYPE_CHECKING:
    from scrapy.http import Response
    from scrapy.http.response.html import HtmlResponse
    from scrapy.http.response.text import TextResponse
    from scrapy.http.response.xml import XmlResponse

    ScrapyResponse = Union[TextResponse, XmlResponse, HtmlResponse, Response]


class DemoMysqlNacosSpider(AyuSpider):
    name = "demo_mysql_nacos"
    allowed_domains = ["blog.csdn.net"]
    start_urls = ["https://blog.csdn.net/"]
    custom_settings = {
        # 开启远程配置服务
        "APP_CONF_MANAGE": True,
        "ITEM_PIPELINES": {
            "ayugespidertools.pipelines.AyuFtyMysqlPipeline": 300,
        },
    }

    @classmethod
    def update_settings(cls, settings):
        """
        这个方法用于将远程应用管理服务设置为 nacos，正常方法应该是在 VIT 下的 .conf 中设置即可，
        而不需要在 spider 中做任何多余操作，就和 demo_three demo_four 一样；

        切记：这部分只是为了功能演示而添加。
        """
        config_parser = configparser.ConfigParser()
        config_parser.read(f"{VIT_DIR}/.conf", encoding="utf-8")
        _remote_conf = {
            "token": config_parser.get("nacos", "token", fallback=None),
            "url": config_parser.get("nacos", "url", fallback=None),
            "format": config_parser.get("nacos", "format", fallback="json"),
            "remote_type": "nacos",
        }

        super().update_settings(settings)
        settings.set("REMOTE_CONFIG", _remote_conf, priority="spider")

    def start_requests(self):
        """get 请求首页，获取项目列表数据"""
        yield Request(
            url="https://blog.csdn.net/phoenix/web/blog/hot-rank?page=0&pageSize=25&type=",
            callback=self.parse_first,
            headers={
                "referer": "https://blog.csdn.net/rank/list",
            },
            dont_filter=True,
        )

    def parse_first(self, response: "ScrapyResponse"):
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

            ArticleInfoItem = AyuItem(
                article_detail_url=DataItem(article_detail_url, "文章详情链接"),
                article_title=DataItem(article_title, "文章标题"),
                comment_count=DataItem(comment_count, "文章评论数量"),
                favor_count=DataItem(favor_count, "文章赞成数量"),
                nick_name=DataItem(nick_name, "文章作者昵称"),
                _table=DataItem("demo_mysql_nacos", "demo_mysql_nacos表"),
            )
            self.slog.info(f"ArticleInfoItem: {ArticleInfoItem}")
            yield ArticleInfoItem
