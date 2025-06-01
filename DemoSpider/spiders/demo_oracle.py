# oracle 场景不会添加自动创建数据库，表及字段等功能，请手动管理
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuSpider
from ayugespidertools.utils.database import OraclePortal
from scrapy.http import Request

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from oracledb import Connection, Cursor

    from DemoSpider.common.types import ScrapyResponse


class DemoOracleSpider(AyuSpider):
    oracle_conn: Connection
    oracle_cursor: Cursor

    name = "demo_oracle"
    allowed_domains = ["readthedocs.io"]
    start_urls = ["https://readthedocs.io"]
    custom_settings = {
        "ITEM_PIPELINES": {
            "ayugespidertools.pipelines.AyuFtyOraclePipeline": 300,
        },
    }

    async def start(self) -> AsyncIterator[Any]:
        self.oracle_conn = OraclePortal(db_conf=self.oracle_conf).connect()
        self.oracle_cursor = self.oracle_conn.cursor()
        yield Request(
            url="https://ayugespidertools.readthedocs.io/en/latest/",
            callback=self.parse_first,
        )

    def parse_first(self, response: ScrapyResponse) -> Any:
        _save_table = "_article_info_list"
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

            sql = f"""select 1 from "{_save_table}" where "octree_text" = '{octree_text}' AND ROWNUM <= 1"""
            self.oracle_cursor.execute(sql)
            exists = self.oracle_cursor.fetchone()
            if exists:
                self.slog.debug(f'标题为 "{octree_text}" 的数据已存在')
            else:
                yield octree_item
