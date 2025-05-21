"""
- 使用 PostgreSQLAsyncPortal 来查询时就需要自己先提前创建好所需的库和表了；也可以删除它，然后
AyuFtyPostgresPipeline 就可以自动创库创表及所需字段了。
- 这里主要是为了展示使用 PostgreSQLAsyncPortal 来查询的示例。
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuSpider
from ayugespidertools.utils.database import PostgreSQLAsyncPortal
from scrapy import signals
from scrapy.http import Request

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from psycopg_pool import AsyncConnectionPool
    from scrapy.crawler import Crawler
    from typing_extensions import Self

    from DemoSpider.common.types import ScrapyResponse


class DemoNineSpider(AyuSpider):
    # 可用于入库前查询使用等场景，名称等可自定义
    psycopg_conn_pool: AsyncConnectionPool

    name = "demo_nine"
    allowed_domains = ["readthedocs.io"]
    start_urls = ["https://readthedocs.io"]
    custom_settings = {
        "ITEM_PIPELINES": {
            "ayugespidertools.pipelines.AyuFtyPostgresPipeline": 300,
        },
    }

    @classmethod
    def from_crawler(cls, crawler: Crawler, *args: Any, **kwargs: Any) -> Self:
        spider = super(DemoNineSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    async def spider_closed(self, spider: AyuSpider) -> None:
        await self.psycopg_conn_pool.close()

    async def start(self) -> AsyncIterator[Any]:
        """get 请求首页，获取项目列表数据"""
        self.psycopg_conn_pool = PostgreSQLAsyncPortal(
            db_conf=self.postgres_conf
        ).connect()
        await self.psycopg_conn_pool.open()
        yield Request(
            url="https://ayugespidertools.readthedocs.io/en/latest/",
            callback=self.parse_first,
        )

    async def parse_first(self, response: ScrapyResponse) -> Any:
        _save_table = "demo_nine"
        li_list = response.xpath('//div[@aria-label="Navigation menu"]/ul/li')
        for curr_li in li_list:
            octree_text = curr_li.xpath("a/text()").get()
            octree_href = curr_li.xpath("a/@href").get()

            octree_item = AyuItem(
                octree_text=octree_text,
                octree_href=octree_href,
                _table=_save_table,
            )
            self.slog.info(f"octree_item: {octree_item}")

            async with self.psycopg_conn_pool.connection() as conn:
                async with conn.cursor() as cursor:
                    sql = f"select id from {_save_table} where octree_text = '{octree_text}' limit 1"
                    await cursor.execute(sql)
                    exists = await cursor.fetchone()
                    if not exists:
                        yield octree_item
                    else:
                        self.slog.debug(f'标题为 "{octree_text}" 的数据已存在')
