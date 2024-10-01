"""
Note:
    将 AyuItem 中的部分字段上传到 oss 的示例一：
    - 这是使用 AyuAsyncOssPipeline 根据 [oss:ali] 中的规则限定来将 AyuItem 中符合规则的
      字段对应的资源上传到 oss 的示例：
    - 规则配置如下:
      - 参数 upload_fields_suffix 为需要上传的字段规则，如果此字段包含此后缀则会上传此网
        络流至 oss，默认为 _file_url；
      - 参数 oss_fields_prefix 为上传至 oss 的字段对应的新 AyuItem 字段名规则，新字段
        会在原字段加上此前缀，默认为 _。

NOTICE:
    - 运行前需要安装 ayugespidertools[all]
    - 虽然方便了开发，但规则限定这种方式不太优雅，不是所有人都喜欢。也可根据 demo_oss_sec 的
      示例自行实现。
"""

import json
from typing import Any, Iterable

from ayugespidertools.common.utils import Tools
from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request

from DemoSpider.common.types import ScrapyResponse


class DemoOssSpider(AyuSpider):
    name = "demo_oss"
    start_urls = [
        "https://cms-api.csdn.net/v1/web_home/select_content?componentIds=www-blog-recommend&cate1=python"
    ]
    custom_settings = {
        "ITEM_PIPELINES": {
            "ayugespidertools.pipelines.AyuAsyncOssPipeline": 300,
            "ayugespidertools.pipelines.AyuFtyMysqlPipeline": 301,
        },
        "CONCURRENT_REQUESTS": 64,
        "DOWNLOAD_DELAY": 0.01,
    }

    def start_requests(self) -> Iterable[Request]:
        yield Request(url=self.start_urls[0], callback=self.parse_first)

    def parse_first(self, response: ScrapyResponse) -> Any:
        _save_table = "demo_oss"

        data_list = json.loads(response.text)["data"]["www-blog-recommend"]["info"]
        for curr_data in data_list:
            # 这里的解析方式可换成你喜欢的风格
            title = Tools.extract_with_json(
                json_data=curr_data, query=["extend", "title"]
            )
            title_pic = Tools.extract_with_json(
                json_data=curr_data, query=["extend", "pic"]
            )
            title_pic = title_pic.split("?x-oss-process")[0] if title_pic else ""

            img_item = AyuItem(
                title=title,
                _table=_save_table,
                # 不再需要对需要上传的字段进行判空处理了，但还是要保证链接的有效性。
                title_pic_file_url=title_pic,
            )
            self.slog.info(f"img_item: {img_item}")
            yield img_item
