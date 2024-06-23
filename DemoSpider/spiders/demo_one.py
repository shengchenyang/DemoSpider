# 存入 Mysql 示例 (配置根据本地 .conf 取值)
from typing import Any, Iterable

# import pandas
from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request
from sqlalchemy import text

from DemoSpider.common.types import ScrapyResponse

# from ayugespidertools.items import DataItem


class DemoOneSpider(AyuSpider):
    name = "demo_one"
    allowed_domains = ["readthedocs.io"]
    start_urls = ["https://readthedocs.io"]
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
        yield Request(
            url="https://ayugespidertools.readthedocs.io/en/latest/",
            callback=self.parse_first,
        )

    def parse_first(self, response: ScrapyResponse) -> Any:
        _save_table = "demo_one"

        li_list = response.xpath('//div[@aria-label="Navigation menu"]/ul/li')
        for curr_li in li_list:
            octree_text = curr_li.xpath("a/text()").get()
            octree_href = curr_li.xpath("a/@href").get()

            # NOTE: 数据存储方式 1，推荐此风格写法。
            octree_item = AyuItem(
                octree_text=octree_text,
                octree_href=octree_href,
                _table=_save_table,
            )

            # NOTE: 数据存储方式 2，需要自动添加表字段注释时的写法。但不要风格混用。
            """
            octree_item = AyuItem(
                # 这里也可以写为 octree_text = DataItem(octree_text)，但没有字段注释
                # 功能了，那不如使用 <数据存储方式 1>
                octree_text=DataItem(octree_text, "标题"),
                octree_href=DataItem(octree_href, "标题链接"),
                _table=DataItem(_save_table, "项目列表信息"),
            )
            """

            # NOTE: 数据存储方式 3，当然也可以直接 yield dict
            # 但 _table，_mongo_update_rule 等参数就没有 IDE 提示功能了
            """
            yield {
                "octree_text": octree_text,
                "octree_href": octree_href,
                "_table": _save_table,
            }
            """
            self.slog.info(f"octree_item: {octree_item}")

            # 数据入库逻辑 -> 测试 mysql_engine / mysql_engine_conn 的去重功能。
            # 场景对应的 engine 和 engine_conn 也已经给你了，你可自行实现。以下给出示例：

            # 示例一：使用 sqlalchemy2 结合 <db>_engine_conn 实现查询如下：
            if self.mysql_engine_conn:
                try:
                    _sql = text(
                        f"select `id` from `{_save_table}` where `octree_text` = {octree_text!r} limit 1"
                    )
                    result = self.mysql_engine_conn.execute(_sql).fetchone()
                    if not result:
                        self.mysql_engine_conn.rollback()
                        yield octree_item
                    else:
                        self.slog.debug(f"标题为 {octree_text!r} 的数据已存在")
                except Exception:
                    self.mysql_engine_conn.rollback()
                    yield octree_item
            else:
                yield octree_item

            # 示例二：使用 pandas 结合对应 <db>_engine 去重的示例：
            """
            try:
                sql = f"select `id` from `{_save_table}` where `octree_text` = {octree_text!r} limit 1"
                df = pandas.read_sql(sql, self.mysql_engine)

                # 如果为空，说明此数据不存在于数据库，则新增
                if df.empty:
                    yield octree_item

                # 如果已存在，1). 若需要更新，请自定义更新数据结构和更新逻辑；2). 若不用更新，则跳过即可。
                else:
                    self.slog.debug(f"标题为 {octree_text!r} 的数据已存在")

            except Exception as e:
                if any(["1146" in str(e), "1054" in str(e), "doesn't exist" in str(e)]):
                    yield octree_item
                else:
                    self.slog.error(f"请查看数据库链接或网络是否通畅！Error: {e}")
            """
