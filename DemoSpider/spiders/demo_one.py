# 热榜文章排名 Demo 采集示例 - 存入 Mysql (配置根据本地 .conf 取值)
import json
from typing import Any, Iterable

from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request
from sqlalchemy import text

from DemoSpider.common.types import ScrapyResponse

# from ayugespidertools.items import DataItem


class DemoOneSpider(AyuSpider):
    name = "demo_one"
    allowed_domains = ["blog.csdn.net"]
    start_urls = ["https://blog.csdn.net/"]
    custom_settings = {
        # 打开数据库引擎开关，用于数据入库前更新逻辑判断
        "DATABASE_ENGINE_ENABLED": True,
        "ITEM_PIPELINES": {
            # 激活此项则数据会存储至 Mysql
            "ayugespidertools.pipelines.AyuFtyMysqlPipeline": 300,
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
        _save_table = "demo_one"
        data_list = json.loads(response.text)["data"]
        for curr_data in data_list:
            article_detail_url = curr_data.get("articleDetailUrl")
            article_title = curr_data.get("articleTitle")
            comment_count = curr_data.get("commentCount")
            favor_count = curr_data.get("favorCount")
            nick_name = curr_data.get("nickName")

            # NOTE: 数据存储方式 1，推荐此风格写法。
            article_item = AyuItem(
                article_detail_url=article_detail_url,
                article_title=article_title,
                comment_count=comment_count,
                favor_count=favor_count,
                nick_name=nick_name,
                _table=_save_table,
            )

            # NOTE: 数据存储方式 2，需要自动添加表字段注释时的写法。但不要风格混用。
            """
            article_item = AyuItem(
                # 这里也可以写为 article_detail_url = DataItem(article_detail_url)，但没有字段
                # 注释功能了，那不如使用 <数据存储方式 1>
                article_detail_url=DataItem(article_detail_url, "文章详情链接"),
                article_title=DataItem(article_title, "文章标题"),
                comment_count=DataItem(comment_count, "文章评论数量"),
                favor_count=DataItem(favor_count, "文章赞成数量"),
                nick_name=DataItem(nick_name, "文章作者昵称"),
                _table=DataItem(_save_table, "项目列表信息"),
            )
            """

            # NOTE: 数据存储方式 3，当然也可以直接 yield dict
            # 但 _table，_mongo_update_rule 等参数就没有 IDE 提示功能了
            """
            yield {
                "article_detail_url": article_detail_url,
                "article_title": article_title,
                "comment_count": comment_count,
                "favor_count": favor_count,
                "nick_name": nick_name,
                "_table": _save_table,
            }
            """

            self.slog.info(f"article_item: {article_item}")
            # yield article_item

            if self.mysql_engine_conn:
                try:
                    _sql = text(
                        f'select `id` from `{_save_table}` where `article_detail_url` = "{article_detail_url}" limit 1'
                    )
                    result = self.mysql_engine_conn.execute(_sql).fetchone()
                    if not result:
                        self.mysql_engine_conn.rollback()
                        yield article_item
                    else:
                        self.slog.debug(f'标题为 "{article_title}" 的数据已存在')
                except Exception:
                    self.mysql_engine_conn.rollback()
                    yield article_item
            else:
                yield article_item

            # 使用 pandas 结合对应 <db>_engine 去重的示例：
            """
            import pandas
            try:
                sql = f'select `id` from `{_save_table}` where `article_detail_url` = "{article_detail_url}" limit 1'
                df = pandas.read_sql(sql, self.mysql_engine)

                # 如果为空，说明此数据不存在于数据库，则新增
                if df.empty:
                    yield article_item

                # 如果已存在，1). 若需要更新，请自定义更新数据结构和更新逻辑；2). 若不用更新，则跳过即可。
                else:
                    self.slog.debug(f"标题为 ”{article_title}“ 的数据已存在")

            except Exception as e:
                if any(["1146" in str(e), "1054" in str(e), "doesn't exist" in str(e)]):
                    yield article_item
                else:
                    self.slog.error(f"请查看数据库链接或网络是否通畅！Error: {e}")
            """
