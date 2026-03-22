"""
根据任务 mq 来获取采集任务，可以很方便地实现分布式部署；
具体文档请查看 https://ayugespidertools.readthedocs.io/en/latest/topics/rabbitspider.html
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ayugespidertools import AyuRabbitMQSpider
from ayugespidertools.items import AyuItem
from scrapy.http import Request

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from scrapy.http.response import Response


class DemoMqTaskSpider(AyuRabbitMQSpider):
    name = "demo_mq_task"

    async def start_requests_from_mq(self, task_info: dict) -> AsyncIterator[Any]:
        # 从任务 mq 中取出具体信息，这里以获取 example_param 为例
        example_param = task_info.get("example_param")
        self.slog.info(f"取出的信息: {example_param}")
        yield Request(
            url="data:,",
            callback=self.parse_first,
            dont_filter=True,
        )

    async def parse_first(self, response: Response) -> Any:
        # 这里具体是推送结果到 mq 结果队列，还是保存到不同数据库 pipeline 中请自行选择；
        # 也可以结合使用。
        _save_table = "demo_mq_task_table"
        yield AyuItem(
            octree_text="octree_text",
            octree_href="octree_href",
            _table="_save_table",
        )
