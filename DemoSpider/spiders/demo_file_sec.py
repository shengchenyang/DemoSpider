import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from ayugespidertools.common.utils import ToolsForAyu
from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request
from scrapy.utils.defer import maybe_deferred_to_future
from twisted.internet.defer import DeferredList

from DemoSpider.common.types import ScrapyResponse


def download(response, file_url, file_path):
    headers_dict = ToolsForAyu.get_dict_form_scrapy_req_headers(
        scrapy_headers=response.headers
    )
    content_type = headers_dict.get("Content-Type")
    file_format = content_type.split("/")[-1].replace("jpeg", "jpg")

    url_hash = hashlib.md5(file_url.encode("utf8")).hexdigest()
    filename = f"{file_path}/{url_hash}.{file_format}"
    Path(filename).write_bytes(response.body)
    return filename


class DemoFileSecSpider(AyuSpider):
    name = "demo_file_sec"
    custom_settings = {
        "ITEM_PIPELINES": {
            "ayugespidertools.pipelines.AyuFtyMysqlPipeline": 300,
        },
        "DOWNLOADER_MIDDLEWARES": {
            "ayugespidertools.middlewares.RandomRequestUaMiddleware": 400,
        },
        # 下载文件保存路径
        "FILES_STORE": Path(__file__).parent.parent / "docs",
    }

    def start_requests(self) -> Iterable[Request]:
        yield Request(
            url="https://cms-api.csdn.net/v1/web_home/select_content?componentIds=www-blog-recommend&cate1=python",
            callback=self.parse_first,
        )

    async def parse_first(self, response: ScrapyResponse) -> Any:
        _save_table = "demo_file_sec"

        data_list = json.loads(response.text)["data"]["www-blog-recommend"]["info"]
        for curr_data in data_list:
            title = ToolsForAyu.extract_with_json(
                json_data=curr_data, query=["extend", "title"]
            )
            title_pic = ToolsForAyu.extract_with_json(
                json_data=curr_data, query=["extend", "pic"]
            )
            avatarurl = ToolsForAyu.extract_with_json(
                json_data=curr_data, query=["extend", "avatarurl"]
            )
            title_pic = title_pic.split("?x-oss-process")[0] if title_pic else ""
            avatarurl = avatarurl.split("?x-oss-process")[0] if avatarurl else ""

            additional_requests = []
            if title_pic:
                title_pic_r = Request(title_pic, cb_kwargs={"key": "title_pic"})
                additional_requests.append(title_pic_r)
            if avatarurl:
                avatarurl_r = Request(avatarurl, cb_kwargs={"key": "avatarurl"})
                additional_requests.append(avatarurl_r)

            deferreds = []
            for r in additional_requests:
                deferred = self.crawler.engine.download(r)
                deferreds.append(deferred)
            responses = await maybe_deferred_to_future(DeferredList(deferreds))

            img_item = AyuItem(
                title=title,
                title_pic=title_pic,
                avatarurl=avatarurl,
                _table=_save_table,
            )
            for response_tuple in responses:
                curr_response = response_tuple[1]
                curr_cb_key = curr_response.cb_kwargs["key"]
                file_name = download(
                    response=curr_response,
                    file_url=img_item[f"{curr_cb_key}"],
                    file_path=self.custom_settings["FILES_STORE"],
                )

                # 这里是需要下载到本地字段的对应本地路径字段名
                # 这里对应的本地路径为原字段名添加 local_ 前缀
                # 比如，原字段为 title_pic，新增的下载路径字段为 local_title_pic
                # 你完全可以自定义
                img_item.add_field(f"local_{curr_cb_key}", file_name)
            self.slog.info(f"img_item: {img_item}")
            yield img_item
