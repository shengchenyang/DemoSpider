# 存入 Mysql 示例 (配置根据本地 .conf 取值)
from __future__ import annotations

import random
from typing import TYPE_CHECKING, Any

from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from DemoSpider.common.types import ScrapyResponse


class DemoOneSpider(AyuSpider):
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
        yield Request(
            url="https://ayugespidertools.readthedocs.io/en/latest/",
            callback=self.parse_first,
        )

    async def parse_first(self, response: ScrapyResponse) -> Any:
        _save_table = "demo_one"

        li_list = response.xpath('//div[@aria-label="Navigation menu"]/ul/li')
        for curr_li in li_list:
            octree_text = curr_li.xpath("a/text()").get()
            # 这里加随机数用于测试更新功能
            octree_href = curr_li.xpath("a/@href").get("") + str(random.randint(0, 100))

            # NOTE: 数据存储方式 1，推荐此风格写法。
            """
            如果你不在意更新场景，那么 _update_rule，_update_keys 和 _conflict_cols 等字段都不用设置！
            """
            octree_item = AyuItem(
                octree_text=octree_text,
                octree_href=octree_href,
                _table=_save_table,
                # 更新逻辑，如果 octree_text 已存在则更新或忽略，不存在会执行插入(需配合唯一索引使用)。
                _update_rule={"octree_text": octree_text},
                # 以 _update_rule 查询条件判断已存在时候，要更新哪些字段。_update_keys 不设置则还是
                # 走新增(注意：在设置了唯一索引时，推荐设置 _update_keys 参数或 insert_ignore 配置
                # 为 true，具体使用方式请按照自己喜欢的来。)
                # 比如此示例，需要在 mysql _table 表设置 octree_text 为唯一索引，插入相同唯一索引
                # 对应的数据会自动触发更新 _update_keys 中的字段，否则就正常新增数据。若你不设置唯一
                # 索引，则会永远执行新增插入。
                # 当然，如果设置了唯一索引且遇到了相同数据，但是并不想走更新逻辑，而是忽略它，那么不设
                # 置 _update_keys 并结合 insert_ignore 即可。
                _update_keys={"octree_href"},
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
            yield octree_item
