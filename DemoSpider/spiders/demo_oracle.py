# oracle 场景不会添加自动创建数据库，表及字段等功能，请手动管理
from typing import Any, Iterable

from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request
from sqlalchemy import text

from DemoSpider.common.types import ScrapyResponse


class DemoOracleSpider(AyuSpider):
    name = "demo_oracle"
    allowed_domains = ["readthedocs.io"]
    start_urls = ["https://readthedocs.io"]
    custom_settings = {
        "DATABASE_ENGINE_ENABLED": True,
        "ITEM_PIPELINES": {
            "ayugespidertools.pipelines.AyuFtyOraclePipeline": 300,
        },
    }

    def start_requests(self) -> Iterable[Request]:
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
            # yield octree_item

            if self.oracle_engine_conn:
                _sql = text(
                    f"""select 1 from "{_save_table}" where "octree_text" = '{octree_text}' AND ROWNUM <= 1"""
                )
                if _ := self.oracle_engine_conn.execute(_sql).fetchone():
                    self.slog.debug(f'标题为 "{octree_text}" 的数据已存在')
                else:
                    yield octree_item
