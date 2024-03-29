import json
from typing import Any, Iterable

from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request
from sqlalchemy import text

from DemoSpider.common.types import ScrapyResponse


class DemoNineSpider(AyuSpider):
    name = "demo_nine"
    allowed_domains = ["csdn.net"]
    start_urls = ["https://blog.csdn.net/"]
    custom_settings = {
        # 打开数据库引擎开关，用于数据入库前更新逻辑判断
        "DATABASE_ENGINE_ENABLED": True,
        "ITEM_PIPELINES": {
            "ayugespidertools.pipelines.AyuFtyPostgresPipeline": 300,
        },
        "DOWNLOADER_MIDDLEWARES": {
            "ayugespidertools.middlewares.RandomRequestUaMiddleware": 400,
        },
    }

    def start_requests(self) -> Iterable[Request]:
        """get 请求首页，获取项目列表数据"""
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
        _save_table = "demo_nine"
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

            # 同样也可使用之前的 pandas 结合对应的 <db>_engine 来去重，各有优缺点。
            # 也可自行实现，本库模版中使用 SQLAlchemy 结合对应 <db>_engine_conn 的方式实现。
            if self.postgres_engine_conn:
                try:
                    _sql = text(
                        f"""select id from {_save_table} where article_detail_url = '{article_detail_url}' limit 1"""
                    )
                    result = self.postgres_engine_conn.execute(_sql).fetchone()
                    if not result:
                        self.postgres_engine_conn.rollback()
                        yield article_item
                    else:
                        self.slog.debug(f'标题为 "{article_title}" 的数据已存在')
                except Exception:
                    self.postgres_engine_conn.rollback()
                    yield article_item
            else:
                yield article_item
