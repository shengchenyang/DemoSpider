"""
Note:
    上传 AyuItem 中的部分资源字段上传到 oss 的示例二：
    更推荐使用这种方法，尽量不要使用本库 oss 相关的 pipeline，虽然本方式看起
来比较繁琐，但是你可以优化并整理一些方法为独立模块使用。其实这样逻辑更明确清晰，
如果不想把上传逻辑放在 spider 中，你也可以仿照着开发所需的 pipeline 模块。

NOTICE:
    运行前先在 __init__ 的部分补充 access_key， access_secret 等参数。
"""
import hashlib
import json
from typing import TYPE_CHECKING, Union

import scrapy
from ayugespidertools.common.utils import ToolsForAyu
from ayugespidertools.extras.oss import AliOssBase
from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request
from scrapy.http.request import NO_CALLBACK
from scrapy.utils.defer import maybe_deferred_to_future
from scrapy.utils.python import to_bytes

if TYPE_CHECKING:
    from scrapy import Spider
    from scrapy.http import Response
    from scrapy.http.response.html import HtmlResponse
    from scrapy.http.response.text import TextResponse
    from scrapy.http.response.xml import XmlResponse

    ScrapyResponse = Union[TextResponse, XmlResponse, HtmlResponse, Response]


async def _download(
    spider: "Spider",
    file_url: str,
):
    request = scrapy.Request(file_url, callback=NO_CALLBACK)
    response = await maybe_deferred_to_future(spider.crawler.engine.download(request))
    headers_dict = ToolsForAyu.get_dict_form_scrapy_req_headers(
        scrapy_headers=response.headers
    )
    content_type = headers_dict.get("Content-Type")
    file_format = content_type.split("/")[-1].replace("jpeg", "jpg")
    file_guid = hashlib.sha1(to_bytes(file_url)).hexdigest()
    filename = f"{file_guid}.{file_format}"
    return response, filename


class DemoOssSecSpider(AyuSpider):
    name = "demo_oss_sec"
    allowed_domains = ["csdn.net"]
    start_urls = [
        "https://cms-api.csdn.net/v1/web_home/select_content?componentIds=www-blog-recommend&cate1=python"
    ]
    custom_settings = {
        "ITEM_PIPELINES": {
            "ayugespidertools.pipelines.AyuFtyMysqlPipeline": 300,
        },
        "CONCURRENT_REQUESTS": 64,
        "DOWNLOAD_DELAY": 0.01,
    }

    def __init__(self):
        # 这里和 _download 方法推荐自行封装成模块使用。
        self.oss_bucket = AliOssBase(
            access_key="xxx",
            access_secret="xxx",
            endpoint="https://xxx.aliyuncs.com",
            bucket="xxx",
            doc="xxx",
        )

    def start_requests(self):
        yield Request(
            url=self.start_urls[0],
            callback=self.parse_first,
            cb_kwargs={
                "curr_site": "csdn",
            },
            dont_filter=True,
        )

    async def parse_first(self, response: "ScrapyResponse", curr_site: str):
        self.slog.info(f"当前采集的站点为: {curr_site}")
        _save_table = "demo_oss_sec"

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
                title_pic=title_pic,
                _table=_save_table,
            )
            if title_pic:
                r, filename = await _download(
                    spider=self.crawler.spider, file_url=title_pic
                )
                self.oss_bucket.put_oss(put_bytes=r.body, file=filename)
                img_item.add_field("oss_title_pic", filename)
            self.slog.info(f"img_item: {img_item}")
            yield img_item
