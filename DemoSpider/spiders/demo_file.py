# 采集 csdn python 热榜的文章列表，并下载图片
import json
from pathlib import Path
from typing import Any, Iterable

from ayugespidertools.common.utils import Tools
from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request

from DemoSpider.common.types import ScrapyResponse


class DemoFileSpider(AyuSpider):
    name = "demo_file"
    start_urls = [
        "https://cms-api.csdn.net/v1/web_home/select_content?componentIds=www-blog-recommend&cate1=python"
    ]
    custom_settings = {
        "ITEM_PIPELINES": {
            "ayugespidertools.pipelines.FilesDownloadPipeline": 300,
            "ayugespidertools.pipelines.AyuFtyMysqlPipeline": 301,
        },
        "DOWNLOADER_MIDDLEWARES": {
            "ayugespidertools.middlewares.RandomRequestUaMiddleware": 400,
        },
        # 下载文件保存路径
        "FILES_STORE": Path(__file__).parent.parent / "docs",
    }

    def start_requests(self) -> Iterable[Request]:
        """
        get 请求首页，获取项目列表数据
        """
        yield Request(url=self.start_urls[0], callback=self.parse_first)

    def parse_first(self, response: ScrapyResponse) -> Any:
        _save_table = "demo_file"

        data_list = json.loads(response.text)["data"]["www-blog-recommend"]["info"]
        for curr_data in data_list:
            title = Tools.extract_with_json(
                json_data=curr_data, query=["extend", "title"]
            )
            img_href = Tools.extract_with_json(
                json_data=curr_data, query=["extend", "pic"]
            )

            img_item = AyuItem(
                title=title,
                img_file_url=img_href,
                _table=_save_table,
            )

            # 同样地，也可以直接返回 dict，但记得 _table 字段
            """
            img_item = {
                "title": title,
                "img_file_url": img_href,
                "_table": _save_table,
            }
            """
            self.slog.info(f"img_item: {img_item}")
            yield img_item
