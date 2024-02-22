"""
Note:
    上传 AyuItem 中的部分资源字段上传到 oss 的示例一：
    这是使用 AyuAsyncOssPipeline 根据 [oss:ali] 中的规则配置来上传 AyuItem
部分资源字段到 oss 的示例，规则配置如下：
    参数 upload_fields_suffix 为需要上传的字段规则，如果此字段包含此后缀则会上传此网络流至 oss，默认为 _file_url；
    参数 oss_fields_prefix 为上传至 oss 的字段对应的新 AyuItem 字段名规则，新字段会在原字段加上此前缀，默认为 _。

NOTICE:
    运行前需要安装 ayugespidertools[all]
    虽然看上去方便了开发，但是规则限定这种方式不优雅，推荐查看 demo_oss_sec 的示例。
"""
import json
from typing import TYPE_CHECKING, Union

from ayugespidertools.common.utils import ToolsForAyu
from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request

if TYPE_CHECKING:
    from scrapy.http import Response
    from scrapy.http.response.html import HtmlResponse
    from scrapy.http.response.text import TextResponse
    from scrapy.http.response.xml import XmlResponse

    ScrapyResponse = Union[TextResponse, XmlResponse, HtmlResponse, Response]


class DemoOssSpider(AyuSpider):
    name = "demo_oss"
    allowed_domains = ["csdn.net"]
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

    def start_requests(self):
        yield Request(
            url=self.start_urls[0],
            callback=self.parse_first,
            cb_kwargs={
                "curr_site": "csdn",
            },
            dont_filter=True,
        )

    def parse_first(self, response: "ScrapyResponse", curr_site: str):
        self.slog.info(f"当前采集的站点为: {curr_site}")
        _save_table = "demo_oss"

        data_list = json.loads(response.text)["data"]["www-blog-recommend"]["info"]
        for curr_data in data_list:
            title = ToolsForAyu.extract_with_json(
                json_data=curr_data, query=["extend", "title"]
            )
            title_pic = ToolsForAyu.extract_with_json(
                json_data=curr_data, query=["extend", "pic"]
            )
            title_pic = title_pic.split("?x-oss-process")[0] if title_pic else ""

            img_item = AyuItem(
                title=title,
                _table=_save_table,
            )
            # title_pic 不直接放入 AyuItem 中，是因为它们可能为空，那就无法下载它们了。
            if title_pic:
                img_item.add_field("title_pic_file_url", title_pic)
            self.slog.info(f"img_item: {img_item}")
            yield img_item