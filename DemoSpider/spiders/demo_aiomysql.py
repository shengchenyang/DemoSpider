# 此场景不会自动创建数据库，数据表，表字段等，请手动管理；但更推荐此写法，效率更高
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuSpider
from ayugespidertools.utils.database import MysqlAsyncPortal
from scrapy.http import Request

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from aiomysql import Pool

    from DemoSpider.common.types import ScrapyResponse


class DemoAiomysqlSpider(AyuSpider):
    # 可用于入库前查询使用等场景
    mysql_conn_pool: Pool

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
        self.mysql_conn_pool = await MysqlAsyncPortal(db_conf=self.mysql_conf).connect()
        # 这里请求十次同样 url 是为了测试示例的简单和示例的稳定性，你可自行测试其它目标网站
        for idx, _ in enumerate(range(10)):
            yield Request(
                url="https://ayugespidertools.readthedocs.io/en/latest/",
                callback=self.parse_first,
                cb_kwargs={"index": idx},
                dont_filter=True,
            )

    async def parse_first(self, response: ScrapyResponse, index: str) -> Any:
        _save_table = "demo_aiomysql"
        li_list = response.xpath('//div[@aria-label="Navigation menu"]/ul/li')
        for curr_li in li_list:
            octree_text = curr_li.xpath("a/text()").get()
            octree_href = curr_li.xpath("a/@href").get()

            # NOTE: 数据存储方式 1，推荐此风格写法。
            octree_item = AyuItem(
                octree_text=octree_text,
                octree_href=octree_href,
                start_index=index,
                _table=_save_table,
            )
            self.slog.info(f"octree_item: {octree_item}")

            # 使用此方法时需要提前建库建表
            async with self.mysql_conn_pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    exists = await cursor.execute(
                        f"SELECT `id` from `{_save_table}` where `octree_text` = {octree_text!r} limit 1"
                    )
                    if not exists:
                        yield octree_item
                    else:
                        self.slog.debug(f'标题为 "{octree_text}" 的数据已存在')
