# 热榜文章排名采集，并推送至 kafka
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from DemoSpider.common.types import ScrapyResponse


class DemoKafkaSpider(AyuSpider):
    name = "demo_kafka"
    allowed_domains = ["readthedocs.io"]
    start_urls = ["https://readthedocs.io"]
    custom_settings = {
        "ITEM_PIPELINES": {
            "ayugespidertools.pipelines.AyuKafkaPipeline": 301,
        },
    }

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
                _table="demo_kafka",
            )
            self.slog.info(f"octree_item: {octree_item}")
            yield octree_item
