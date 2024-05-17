# 同时存入 Mysql 和 MongoDB 的场景（其它各种结合场景不再举例）
from typing import Any, Iterable

from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request

from DemoSpider.common.types import ScrapyResponse


class DemoEightSpider(AyuSpider):
    name = "demo_eight"
    allowed_domains = ["readthedocs.io"]
    start_urls = ["https://readthedocs.io"]
    custom_settings = {
        "ITEM_PIPELINES": {
            "ayugespidertools.pipelines.AyuFtyMysqlPipeline": 300,
            "ayugespidertools.pipelines.AyuFtyMongoPipeline": 301,
        },
    }

    def start_requests(self) -> Iterable[Request]:
        yield Request(
            url="https://ayugespidertools.readthedocs.io/en/latest/",
            callback=self.parse_first,
        )

    def parse_first(self, response: ScrapyResponse) -> Any:
        li_list = response.xpath('//div[@aria-label="Navigation menu"]/ul/li')
        for curr_li in li_list:
            octree_text = curr_li.xpath("a/text()").get()
            octree_href = curr_li.xpath("a/@href").get()
            yield AyuItem(
                octree_text=octree_text,
                octree_href=octree_href,
                _table="demo_eight",
            )
