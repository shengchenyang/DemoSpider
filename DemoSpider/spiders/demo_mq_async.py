"""
运行前需要先 pip install ayugespidertools[database]
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from DemoSpider.common.types import ScrapyResponse


class DemoMqAsyncSpider(AyuSpider):
    name = "demo_mq_async"
    allowed_domains = ["readthedocs.io"]
    start_urls = ["https://readthedocs.io"]
    custom_settings = {
        "ITEM_PIPELINES": {
            "ayugespidertools.pipelines.AyuAsyncMQPipeline": 300,
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

            # 推荐返回格式，返回其他格式也是可以的。具体请参考 demo_mq
            yield AyuItem(
                octree_text=octree_text,
                octree_href=octree_href,
                # 这里的 _table 指保存到 mq 的队列名，此值优先级大于 .conf 中 [mq] 的 queue，
                # 用于 spider 中可能推送到多个不同队列的需求。
                # _table="demo_mq_table",
            )
