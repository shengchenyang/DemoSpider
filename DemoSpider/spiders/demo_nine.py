"""
- 使用 PostgreSQLAsyncPortal 来查询时就需要自己先提前创建好所需的库和表了；也可以删除它，然后
AyuFtyPostgresPipeline 就可以自动创库创表及所需字段了。
- 这里主要是为了展示使用 PostgreSQLAsyncPortal 来查询的示例。
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, Any

from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from DemoSpider.common.types import ScrapyResponse


class DemoNineSpider(AyuSpider):
    name = "demo_nine"
    allowed_domains = ["readthedocs.io"]
    start_urls = ["https://readthedocs.io"]
    custom_settings = {
        "ITEM_PIPELINES": {
            "ayugespidertools.pipelines.AyuFtyPostgresPipeline": 300,
        },
    }

    async def start(self) -> AsyncIterator[Any]:
        """get 请求首页，获取项目列表数据"""
        yield Request(
            url="https://ayugespidertools.readthedocs.io/en/latest/",
            callback=self.parse_first,
        )

    async def parse_first(self, response: ScrapyResponse) -> Any:
        # 也可以直接写 demo_nine，pg 默认 public
        _save_table = "public.demo_nine"
        li_list = response.xpath('//div[@aria-label="Navigation menu"]/ul/li')
        for curr_li in li_list:
            octree_text = curr_li.xpath("a/text()").get()
            octree_href = curr_li.xpath("a/@href").get("") + str(random.randint(0, 100))

            # 更新逻辑使用方法大致和 demo_one 的 mysql 一样，只是多了个 _conflict_cols 字段来指定
            # 唯一索引字段(用于在设置了唯一索引时指定此字段来实现 upsert 功能)，至于为什么不使用
            # MERGE INTO 就可以不用指定 _conflict_cols 了呢？因为此语法最低需要 postgresql 15
            # 才能支持，为了兼容性考虑。
            # 注意：没有设置唯一索引就不能设置 _conflict_cols 参数。
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
