from typing import Any, Iterable

from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request

from DemoSpider.common.types import ScrapyResponse


class DemoTenSpider(AyuSpider):
    name = "demo_ten"
    allowed_domains = ["readthedocs.io"]
    start_urls = ["https://readthedocs.io"]
    custom_settings = {
        "DATABASE_ENGINE_ENABLED": True,
        "ITEM_PIPELINES": {
            "ayugespidertools.pipelines.AyuTwistedPostgresPipeline": 300,
        },
        "DOWNLOADER_MIDDLEWARES": {
            "ayugespidertools.middlewares.RandomRequestUaMiddleware": 400,
        },
        "CONCURRENT_REQUESTS": 64,
        "DOWNLOAD_DELAY": 0.01,
    }

    def start_requests(self) -> Iterable[Request]:
        # 这里请求十次同样 url 是为了测试示例的简单和示例的稳定性，你可自行测试其它目标网站
        for idx, _ in enumerate(range(10)):
            yield Request(
                url="https://ayugespidertools.readthedocs.io/en/latest/",
                callback=self.parse_first,
                cb_kwargs={"index": idx},
                dont_filter=True,
            )

    def parse_first(self, response: ScrapyResponse, index: str) -> Any:
        _save_table = "demo_ten"

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
            yield octree_item
