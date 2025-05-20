# 存入 Mysql 示例 (配置根据本地 .conf 取值)
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuSpider
from ayugespidertools.utils.database import MysqlAsyncPortal
from scrapy.http import Request

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from aiomysql import Pool

    from DemoSpider.common.types import ScrapyResponse


class DemoOneSpider(AyuSpider):
    # 可用于入库前查询使用等场景，名称等可自定义
    mysql_conn_pool: Pool

    name = "demo_one"
    allowed_domains = ["readthedocs.io"]
    start_urls = ["https://readthedocs.io"]
    custom_settings = {
        "ITEM_PIPELINES": {
            # 激活此项则数据会存储至 Mysql
            "ayugespidertools.pipelines.AyuFtyMysqlPipeline": 300,
        },
        "DOWNLOADER_MIDDLEWARES": {
            # 随机请求头
            "ayugespidertools.middlewares.RandomRequestUaMiddleware": 400,
        },
    }

    async def start(self) -> AsyncIterator[Any]:
        self.mysql_conn_pool = await MysqlAsyncPortal(db_conf=self.mysql_conf).connect()
        yield Request(
            url="https://ayugespidertools.readthedocs.io/en/latest/",
            callback=self.parse_first,
        )

    async def parse_first(self, response: ScrapyResponse) -> Any:
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

            # 数据入库逻辑 -> 测试 ayugespidertools.utils.database.MysqlAsyncPortal 的去重功能。
            # 使用此方法时需要提前建库建表
            async with self.mysql_conn_pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    exists = await cursor.execute(
                        f"SELECT `id` from `{_save_table}` where `octree_text` = {octree_text!r} limit 1"
                    )
                    if not exists:
                        yield octree_item
                    else:
                        self.slog.debug(f'标题为 "{octree_text}" 的数据已存在')
