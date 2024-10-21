"""
NOTE:
    - elasticsearch 同步存储场景
    - 需要安装 ayugespidertools[database]
"""

from typing import Any, Iterable

from ayugespidertools.items import AyuItem, DataItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request

from DemoSpider.common.types import ScrapyResponse

try:
    from elasticsearch_dsl import Keyword, Search, Text
except ImportError:
    # pip install ayugespidertools[database]
    pass


class DemoEsSpider(AyuSpider):
    name = "demo_es"
    allowed_domains = ["readthedocs.io"]
    start_urls = ["https://readthedocs.io"]
    custom_settings = {
        "DATABASE_ENGINE_ENABLED": True,
        "ITEM_PIPELINES": {
            "ayugespidertools.pipelines.AyuFtyESPipeline": 300,
        },
        "DOWNLOADER_MIDDLEWARES": {
            "ayugespidertools.middlewares.RandomRequestUaMiddleware": 400,
        },
    }

    def start_requests(self) -> Iterable[Request]:
        yield Request(
            url="https://ayugespidertools.readthedocs.io/en/latest/",
            callback=self.parse_first,
        )

    def parse_first(self, response: ScrapyResponse) -> Any:
        _save_table = "demo_es"

        li_list = response.xpath('//div[@aria-label="Navigation menu"]/ul/li')
        for curr_li in li_list:
            octree_text = curr_li.xpath("a/text()").get()
            octree_href = curr_li.xpath("a/@href").get()

            octree_item = AyuItem(
                octree_text=DataItem(
                    octree_text, Text(analyzer="snowball", fields={"raw": Keyword()})
                ),
                octree_href=DataItem(octree_href, Keyword()),
                _table=DataItem(_save_table),
            )
            self.slog.info(f"octree_item: {octree_item}")
            # 查重逻辑自己设置，精确匹配还是全文搜索请自行设置，这里只是一种示例。
            # 请自定义查重和更新方式，比如使用查询并更新的语句。
            s = (
                Search(using=self.es_engine, index=_save_table)
                .query("term", octree_href=octree_href)
                .execute()
            )
            if s.hits.total.value > 0:
                self.slog.debug(f'链接为 "{octree_href}" 的数据已存在')
            else:
                yield octree_item
