import json

from ayugespidertools.common.utils import ToolsForAyu
from ayugespidertools.items import AyuItem, DataItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request
from scrapy.http.response.text import TextResponse

from DemoSpider.items import TableEnum
from DemoSpider.settings import DOC_DIR

"""
####################################################################################################
# collection_website: csdn.net - csdn python 热榜
# collection_content: 采集 csdn python 热榜的文章列表，并下载图片
# create_time: 2023-06-19
# explain:
# demand_code_prefix = ""
####################################################################################################
"""


class DemoFileSpider(AyuSpider):
    name = "demo_file"
    allowed_domains = ["csdn.net"]
    start_urls = [
        "https://cms-api.csdn.net/v1/web_home/select_content?componentIds=www-blog-recommend&cate1=python"
    ]

    custom_table_enum = TableEnum
    custom_settings = {
        "ITEM_PIPELINES": {
            "ayugespidertools.pipelines.FilesDownloadPipeline": 300,
            "ayugespidertools.pipelines.AyuFtyMysqlPipeline": 301,
        },
        "DOWNLOADER_MIDDLEWARES": {
            "ayugespidertools.middlewares.RandomRequestUaMiddleware": 400,
        },
        # 下载文件保存路径，不配置则默认为设置中的 DOC_DIR（需要确认此文件夹是否存在）
        "FILES_STORE": DOC_DIR,
    }

    # 打开 mysql 引擎开关，用于数据入库前更新逻辑判断
    mysql_engine_enabled = True

    def start_requests(self):
        """
        get 请求首页，获取项目列表数据
        """
        yield Request(
            url=self.start_urls[0],
            callback=self.parse_first,
            cb_kwargs={
                "curr_site": "csdn",
            },
            dont_filter=True,
        )

    def parse_first(self, response: TextResponse, curr_site: str):
        self.slog.info(f"当前采集的站点为: {curr_site}")

        data_list = json.loads(response.text)["data"]["www-blog-recommend"]["info"]
        for curr_data in data_list:
            title = ToolsForAyu.extract_with_json(
                json_data=curr_data, query=["extend", "title"]
            )
            img_href = ToolsForAyu.extract_with_json(
                json_data=curr_data, query=["extend", "pic"]
            )

            img_item = AyuItem(
                title=DataItem(title, "标题"),
                file_url=DataItem(img_href, "图片链接"),
                file_format=DataItem("png", "图片格式"),
                _table=TableEnum.article_list_table.value["value"],
            )
            self.slog.info(f"img_item: {img_item}")
            yield img_item
