# 热榜文章排名 Demo 采集示例 - 内容推送到 RabbitMQ
import json
from typing import Any, Iterable

from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request

from DemoSpider.common.types import ScrapyResponse


class DemoMqSpider(AyuSpider):
    name = "demo_mq"
    allowed_domains = ["blog.csdn.net"]
    start_urls = ["https://blog.csdn.net/"]
    custom_settings = {
        "ITEM_PIPELINES": {
            "ayugespidertools.pipelines.AyuMQPipeline": 300,
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
            cb_kwargs={
                "curr_site": "csdn",
            },
            dont_filter=True,
        )

    def parse_first(self, response: ScrapyResponse, curr_site: str) -> Any:
        self.slog.info(f"当前采集的站点为: {curr_site}")

        # 你可以自定义解析规则，使用 lxml 还是 response.css response.xpath 等等都可以。
        data_list = json.loads(response.text)["data"]
        for curr_data in data_list:
            article_detail_url = curr_data.get("articleDetailUrl")
            article_title = curr_data.get("articleTitle")
            comment_count = curr_data.get("commentCount")
            favor_count = curr_data.get("favorCount")
            nick_name = curr_data.get("nickName")

            yield {
                "article_detail_url": article_detail_url,
                "article_title": article_title,
                "comment_count": comment_count,
                "favor_count": favor_count,
                "nick_name": nick_name,
                "_table": "demo_mq",
            }

            # 当然，返回其他格式也是可以的。具体请参考 demo_one:
            """
            from ayugespidertools.items import AyuItem, DataItem

            yield AyuItem(
                article_detail_url=DataItem(article_detail_url, "文章详情链接"),
                article_title=DataItem(article_title, "文章标题"),
                comment_count=DataItem(comment_count, "文章评论数量"),
                favor_count=DataItem(favor_count, "文章赞成数量"),
                nick_name=DataItem(nick_name, "文章作者昵称"),
                _table=DataItem("demo_mq", "项目列表信息"),
            )
            """
