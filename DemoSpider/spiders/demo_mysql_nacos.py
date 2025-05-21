# 存储至 mysql 场景，配置从 nacos 获取
from __future__ import annotations

import configparser
from typing import TYPE_CHECKING, Any

from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request
from scrapy.settings import Settings

from DemoSpider.settings import VIT_DIR

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from DemoSpider.common.types import ScrapyResponse


class DemoMysqlNacosSpider(AyuSpider):
    name = "demo_mysql_nacos"
    allowed_domains = ["readthedocs.io"]
    start_urls = ["https://readthedocs.io"]
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

    async def start(self) -> AsyncIterator[Any]:
        yield Request(
            url="https://ayugespidertools.readthedocs.io/en/latest/",
            callback=self.parse_first,
        )

    def parse_first(self, response: ScrapyResponse) -> Any:
        li_list = response.xpath('//div[@aria-label="Navigation menu"]/ul/li')
        for curr_li in li_list:
            octree_text = curr_li.xpath("a/text()").get()
            octree_href = curr_li.xpath("a/@href").get()

            octree_item = AyuItem(
                octree_text=octree_text,
                octree_href=octree_href,
                _table="demo_mysql_nacos",
            )
            self.slog.info(f"octree_item: {octree_item}")
            yield octree_item
