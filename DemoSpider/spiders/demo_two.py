# 存入 MongoDB 示例（配置根据本地 .conf 取值）
import json
from typing import Any, Iterable

from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request

from DemoSpider.common.types import ScrapyResponse


class DemoTwoSpider(AyuSpider):
    name = "demo_two"
    allowed_domains = ["csdn.net"]
    start_urls = ["https://blog.csdn.net/"]
    custom_settings = {
        "ITEM_PIPELINES": {
            # 激活此项则数据会存储至 MongoDB
            "ayugespidertools.pipelines.AyuFtyMongoPipeline": 300,
        },
        "DOWNLOADER_MIDDLEWARES": {
            # 随机请求头
            "ayugespidertools.middlewares.RandomRequestUaMiddleware": 400,
        },
    }

    def start_requests(self) -> Iterable[Request]:
        """
        get 请求首页，获取项目列表数据
        """
        yield Request(
            url="https://blog.csdn.net/phoenix/web/blog/hot-rank?page=0&pageSize=25&type=",
            callback=self.parse_first,
            headers={
                "referer": "https://blog.csdn.net/rank/list",
            },
            dont_filter=True,
        )

    def parse_first(self, response: ScrapyResponse) -> Any:
        data_list = json.loads(response.text)["data"]
        for curr_data in data_list:
            article_detail_url = curr_data.get("articleDetailUrl")
            article_title = curr_data.get("articleTitle")
            comment_count = curr_data.get("commentCount")
            favor_count = curr_data.get("favorCount")
            nick_name = curr_data.get("nickName")

            article_item = AyuItem(
                article_detail_url=article_detail_url,
                article_title=article_title,
                comment_count=comment_count,
                favor_count=favor_count,
                nick_name=nick_name,
                _table="demo_two",
                _mongo_update_rule={"article_detail_url": article_detail_url},
            )

            self.slog.info(f"article_item: {article_item}")
            yield article_item
