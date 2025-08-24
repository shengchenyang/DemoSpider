# oracle 场景不会添加自动创建数据库，表及字段等功能，请手动管理
from __future__ import annotations

import random
from typing import TYPE_CHECKING, Any

from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from DemoSpider.common.types import ScrapyResponse


class DemoOracleSpider(AyuSpider):
    name = "demo_oracle"
    allowed_domains = ["readthedocs.io"]
    start_urls = ["https://readthedocs.io"]
    custom_settings = {
        "ITEM_PIPELINES": {
            "ayugespidertools.pipelines.AyuFtyOraclePipeline": 300,
        },
    }

    async def start(self) -> AsyncIterator[Any]:
        yield Request(
            url="https://ayugespidertools.readthedocs.io/en/latest/",
            callback=self.parse_first,
        )

    def parse_first(self, response: ScrapyResponse) -> Any:
        _save_table = "_article_info_list_no_key"
        li_list = response.xpath('//div[@aria-label="Navigation menu"]/ul/li')
        for curr_li in li_list:
            octree_text = curr_li.xpath("a/text()").get()
            octree_href = curr_li.xpath("a/@href").get("") + str(random.randint(0, 100))

            octree_item = AyuItem(
                octree_text=octree_text,
                octree_href=octree_href,
                _table=_save_table,
                _update_rule={"octree_text": octree_text},
                _update_keys={"octree_href"},
                _conflict_cols={"octree_text"},
            )
            self.slog.info(f"octree_item: {octree_item}")
            yield octree_item
