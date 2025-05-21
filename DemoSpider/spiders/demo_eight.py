"""
同时存入 Mysql 和 MongoDB 的场景（其它各种结合场景不再举例）
可以使用 ayugespidertools.pipelines.AyuFtyMysqlPipeline 的 pipeline 就可以不用手动创建 mysql 数
据库及数据表了，但我还是推荐使用当前配置更高效。
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from DemoSpider.common.types import ScrapyResponse


class DemoEightSpider(AyuSpider):
    name = "demo_eight"
    allowed_domains = ["readthedocs.io"]
    start_urls = ["https://readthedocs.io"]
    custom_settings = {
        "ITEM_PIPELINES": {
            "ayugespidertools.pipelines.AyuAsyncMysqlPipeline": 300,
            "ayugespidertools.pipelines.AyuAsyncMongoPipeline": 301,
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
            yield AyuItem(
                octree_text=octree_text,
                octree_href=octree_href,
                _table="demo_eight",
            )
