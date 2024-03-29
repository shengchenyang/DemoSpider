# oracle 场景不会添加自动创建数据库，表及字段等功能，请手动管理
import json
from typing import Any, Iterable

from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request
from sqlalchemy import text

from DemoSpider.common.types import ScrapyResponse


class DemoOracleSpider(AyuSpider):
    name = "demo_oracle"
    allowed_domains = ["blog.csdn.net"]
    start_urls = ["https://blog.csdn.net/"]
    custom_settings = {
        "DATABASE_ENGINE_ENABLED": True,
        "ITEM_PIPELINES": {
            "ayugespidertools.pipelines.AyuFtyOraclePipeline": 300,
        },
    }

    def start_requests(self) -> Iterable[Request]:
        """请求首页，获取项目列表数据"""
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
        _save_table = "_article_info_list"
        self.slog.info(f"当前采集的站点为: {curr_site}")

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
                _table=_save_table,
            )
            self.slog.info(f"article_item: {article_item}")
            # yield article_item

            if self.oracle_engine_conn:
                _sql = text(
                    f"""select 1 from "{_save_table}" where "article_detail_url" = '{article_detail_url}' AND ROWNUM <= 1"""
                )
                if _ := self.oracle_engine_conn.execute(_sql).fetchone():
                    self.slog.debug(f'标题为 "{article_title}" 的数据已存在')
                else:
                    yield article_item
