# 存储至 mysql 场景，配置从 nacos 获取
import configparser
import json
from typing import Any, Iterable

from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request
from scrapy.settings import Settings

from DemoSpider.common.types import ScrapyResponse
from DemoSpider.settings import VIT_DIR


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
    def update_settings(cls, settings: Settings) -> None:
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

    def start_requests(self) -> Iterable[Request]:
        """get 请求首页，获取项目列表数据"""
        yield Request(
            url="https://blog.csdn.net/phoenix/web/blog/hot-rank?page=0&pageSize=25&type=",
            callback=self.parse_first,
            headers={
                "referer": "https://blog.csdn.net/rank/list",
            },
        )

    def parse_first(self, response: ScrapyResponse) -> Any:
        data_list = json.loads(response.text)["data"]
        for curr_data in data_list:
            article_detail_url = curr_data.get("articleDetailUrl")
            article_title = curr_data.get("articleTitle")
            comment_count = curr_data.get("commentCount")
            favor_count = curr_data.get("favorCount")
            nick_name = curr_data.get("nickName")

            article_item = AyuItem(
                article_detail_url=article_detail_url,
                article_title=article_title,
                comment_count=comment_count,
                favor_count=favor_count,
                nick_name=nick_name,
                _table="demo_mysql_nacos",
            )
            self.slog.info(f"article_item: {article_item}")
            yield article_item
