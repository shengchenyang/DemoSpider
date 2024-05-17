# 热榜文章排名 Demo 采集示例 - 内容推送到 RabbitMQ
from typing import Any, Iterable

from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request

from DemoSpider.common.types import ScrapyResponse


class DemoMqSpider(AyuSpider):
    name = "demo_mq"
    allowed_domains = ["readthedocs.io"]
    start_urls = ["https://readthedocs.io"]
    custom_settings = {
        "ITEM_PIPELINES": {
            "ayugespidertools.pipelines.AyuMQPipeline": 300,
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

            yield {
                "octree_text": octree_text,
                "octree_href": octree_href,
                "_table": "demo_mq",
            }

            # 当然，返回其他格式也是可以的。具体请参考 demo_one:
            """
            from ayugespidertools.items import AyuItem, DataItem

            yield AyuItem(
                octree_text=DataItem(octree_text, "文章详情链接"),
                octree_href=DataItem(octree_href, "文章标题"),
                _table=DataItem("demo_mq", "项目列表信息"),
            )
            """
