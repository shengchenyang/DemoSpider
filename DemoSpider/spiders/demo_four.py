from ayugespidertools.common.utils import ToolsForAyu
from ayugespidertools.items import DataItem, MongoDataItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request

from DemoSpider.items import TableEnum

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
        # 是否开启 consul 的应用管理中心取值的功能(也需要设置 CONSUL_CONF 的值，本示例在 settings 中配置)
        "APP_CONF_MANAGE": True,
        # 数据表的前缀名称，用于标记属于哪个项目（也可不配置此参数，按需配置）
        "MONGODB_COLLECTION_PREFIX": "demo4_",
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

            # ayugespidertools 推荐的风格写法(更直观)
            article_info = {
                "article_detail_url": DataItem(article_detail_url, "文章详情链接"),
                "article_title": DataItem(article_title, "文章标题"),
                "comment_count": DataItem(comment_count, "文章评论数量"),
                "favor_count": DataItem(favor_count, "文章赞成数量"),
                "nick_name": DataItem(nick_name, "文章作者昵称"),
            }

            ArticleInfoItem = MongoDataItem(
                # alldata 用于存储 mongo 的 Document 文档所需要的字段映射
                alldata=article_info,
                # table 为 mongo 的存储 Collection 集合的名称
                table=TableEnum.article_list_table.value["value"],
                # mongo_update_rule 为查询数据是否存在的规则
                mongo_update_rule={"article_detail_url": article_detail_url},
            )
            self.slog.info(f"ArticleInfoItem: {ArticleInfoItem}")
            yield ArticleInfoItem
