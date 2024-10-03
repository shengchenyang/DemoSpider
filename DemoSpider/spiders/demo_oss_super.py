"""
Note:
    - 将 AyuItem 中有关文件资源字段上传到 oss 并存储至 mongodb 的示例，字段支持 list 类型；
    - 规则同 demo_oss demo_oss_sec 一样，这里不再重复；
    - 若存储 mysql 等场景也想支持 list 类型，需自行实现，为了模版统一暂不提供。

NOTICE:
    - 目前是 preview 功能示例，可先自行构建测试。
    - 常规场景中 oss 管道优先级要高于存储
"""

import json
from typing import Any, Iterable

from ayugespidertools.common.utils import Tools
from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request

from DemoSpider.common.types import ScrapyResponse


class DemoOssSuperSpider(AyuSpider):
    name = "demo_oss_super"
    start_urls = [
        "https://cms-api.csdn.net/v1/web_home/select_content?componentIds=www-blog-recommend&cate1=python"
    ]
    custom_settings = {
        "ITEM_PIPELINES": {
            "ayugespidertools.pipelines.AyuAsyncOssBatchPipeline": 300,
            "ayugespidertools.pipelines.AyuAsyncMongoPipeline": 301,
        },
        "CONCURRENT_REQUESTS": 64,
        "DOWNLOAD_DELAY": 0.01,
    }

    def start_requests(self) -> Iterable[Request]:
        yield Request(url=self.start_urls[0], callback=self.parse_first)

    def parse_first(self, response: ScrapyResponse) -> Any:
        _save_table = "demo_oss_mongo"

        data_list = json.loads(response.text)["data"]["www-blog-recommend"]["info"]
        for curr_data in data_list:
            # 这里的解析方式可换成你喜欢的风格
            title = Tools.extract_with_json(
                json_data=curr_data, query=["extend", "title"]
            )
            title_pic = Tools.extract_with_json(
                json_data=curr_data, query=["extend", "pic"]
            )
            avatarurl_pic = Tools.extract_with_json(
                json_data=curr_data, query=["extend", "avatarurl"]
            )
            # 处理下资源链接
            title_pic = title_pic.split("?x-oss-process")[0] if title_pic else ""
            avatarurl_pic = avatarurl_pic.split("!")[0] if title_pic else ""

            img_item = AyuItem(
                title=title,
                # 不再需要对需要上传的字段进行判空处理了，但还是要保证链接的有效性。
                title_pic_file_url=[title_pic, avatarurl_pic],
                _table=_save_table,
            )
            self.slog.info(f"img_item: {img_item}")
            yield img_item
