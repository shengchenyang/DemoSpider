# 此场景不会自动创建数据库，数据表，表字段等，请手动管理；但更推荐此写法，效率更高
from __future__ import annotations

import random
from typing import TYPE_CHECKING, Any

from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from DemoSpider.common.types import ScrapyResponse


class DemoAiomysqlSpider(AyuSpider):
    name = "demo_aiomysql"
    allowed_domains = ["readthedocs.io"]
    start_urls = ["https://readthedocs.io"]
    custom_settings = {
        "ITEM_PIPELINES": {
            # 激活此项则数据会存储至 Mysql，使用 aiomysql 实现
            "ayugespidertools.pipelines.AyuAsyncMysqlPipeline": 300,
        },
        "CONCURRENT_REQUESTS": 64,
        "DOWNLOAD_DELAY": 0.01,
    }

    async def start(self) -> AsyncIterator[Any]:
        # 这里请求十次同样 url 是为了测试示例的简单和示例的稳定性，也是为了测试更新功能是否正常，你也可
        # 自行测试其它目标网站。
        for idx, _ in enumerate(range(10)):
            yield Request(
                url="https://ayugespidertools.readthedocs.io/en/latest/",
                callback=self.parse_first,
                cb_kwargs={"index": idx},
                dont_filter=True,
            )

    async def parse_first(self, response: ScrapyResponse, index: int) -> Any:
        _save_table = "demo_aiomysql"
        li_list = response.xpath('//div[@aria-label="Navigation menu"]/ul/li')
        for curr_li in li_list:
            octree_text = curr_li.xpath("a/text()").get()
            # 这里加随机数用于测试更新功能
            octree_href = curr_li.xpath("a/@href").get("") + str(random.randint(0, 100))

            # 更新逻辑介绍请在 demo_one 中查看
            octree_item = AyuItem(
                octree_text=octree_text,
                octree_href=octree_href,
                start_index=index,
                _table=_save_table,
                _update_rule={"octree_text": octree_text},
                _update_keys={"octree_href"},
            )
            self.slog.info(f"octree_item: {octree_item}")
            yield octree_item
