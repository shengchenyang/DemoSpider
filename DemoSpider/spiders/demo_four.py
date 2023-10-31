from ayugespidertools.common.utils import ToolsForAyu
from ayugespidertools.items import AyuItem, DataItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request

"""
########################################################################################################################
# collection_website: CSDN - 专业开发者社区
# collection_content: 热榜文章排名 Demo 采集示例 - 存入 MongoDB (配置根据 consul 的应用管理中心中取值)
# create_time: 2022-08-02
# explain:
# demand_code_prefix = ""
########################################################################################################################
"""


class DemoFourSpider(AyuSpider):
    name = "demo_four"
    allowed_domains = ["blog.csdn.net"]
    start_urls = ["https://blog.csdn.net/"]
    custom_settings = {
        # 开启远程配置服务(优先级 consul > nacos)
        "APP_CONF_MANAGE": True,
        "ITEM_PIPELINES": {
            # 激活此项则数据会存储至 MongoDB
            "ayugespidertools.pipelines.AyuFtyMongoPipeline": 300,
        },
        "DOWNLOADER_MIDDLEWARES": {
            # 随机请求头
            "ayugespidertools.middlewares.RandomRequestUaMiddleware": 400,
        },
    }

    def start_requests(self):
        """
        get 请求首页，获取项目列表数据
        """
        yield Request(
            url="https://blog.csdn.net/phoenix/web/blog/hot-rank?page=0&pageSize=25&type=",
            callback=self.parse_first,
            headers={
                "referer": "https://blog.csdn.net/rank/list",
            },
            dont_filter=True,
        )

    def parse_first(self, response):
        data_list = ToolsForAyu.extract_with_json(
            json_data=response.json(), query="data"
        )
        for curr_data in data_list:
            article_detail_url = ToolsForAyu.extract_with_json(
                json_data=curr_data, query="articleDetailUrl"
            )
            article_title = ToolsForAyu.extract_with_json(
                json_data=curr_data, query="articleTitle"
            )
            comment_count = ToolsForAyu.extract_with_json(
                json_data=curr_data, query="commentCount"
            )
            favor_count = ToolsForAyu.extract_with_json(
                json_data=curr_data, query="favorCount"
            )
            nick_name = ToolsForAyu.extract_with_json(
                json_data=curr_data, query="nickName"
            )

            ArticleInfoItem = AyuItem(
                article_detail_url=article_detail_url,
                article_title=article_title,
                comment_count=comment_count,
                favor_count=favor_count,
                nick_name=nick_name,
                _table="demo_four",
                _mongo_update_rule={"article_detail_url": article_detail_url},
            )
            self.slog.info(f"ArticleInfoItem: {ArticleInfoItem}")
            yield ArticleInfoItem
