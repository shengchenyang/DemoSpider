from typing import Any, Iterable

from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request
from sqlalchemy import text

from DemoSpider.common.types import ScrapyResponse


class DemoNineSpider(AyuSpider):
    name = "demo_nine"
    allowed_domains = ["readthedocs.io"]
    start_urls = ["https://readthedocs.io"]
    custom_settings = {
        # 打开数据库引擎开关，用于数据入库前更新逻辑判断
        "DATABASE_ENGINE_ENABLED": True,
        "ITEM_PIPELINES": {
            "ayugespidertools.pipelines.AyuFtyPostgresPipeline": 300,
        },
    }

    def start_requests(self) -> Iterable[Request]:
        """get 请求首页，获取项目列表数据"""
        yield Request(
            url="https://ayugespidertools.readthedocs.io/en/latest/",
            callback=self.parse_first,
        )

    def parse_first(self, response: ScrapyResponse) -> Any:
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
            # yield octree_item

            # 同样也可使用之前的 pandas 结合对应的 <db>_engine 来去重，各有优缺点。
            # 也可自行实现，本库模版中使用 SQLAlchemy 结合对应 <db>_engine_conn 的方式实现。
            if self.postgres_engine_conn:
                try:
                    _sql = text(
                        f"select id from {_save_table} where octree_text = '{octree_text}' limit 1"
                    )
                    result = self.postgres_engine_conn.execute(_sql).fetchone()
                    if not result:
                        self.postgres_engine_conn.rollback()
                        yield octree_item
                    else:
                        self.slog.debug(f'标题为 "{octree_text}" 的数据已存在')
                except Exception:
                    self.postgres_engine_conn.rollback()
                    yield octree_item
            else:
                yield octree_item
