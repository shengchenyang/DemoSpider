from ayugespidertools.AyugeSpider import AyuSpider
from ayugespidertools.common.Utils import ToolsForAyu
from ayugespidertools.Items import DataItem, MongoDataItem
from scrapy.http import Request

from DemoSpider.common.DataEnum import TableEnum

"""
########################################################################################################################
# collection_website: CSDN - 专业开发者社区
# collection_content: 热榜文章排名 Demo 采集示例 - 存入 MongoDB (配置根据本地 settings 的 LOCAL_MONGODB_CONFIG 中取值)
# create_time: 2022-08-02
# explain:
# demand_code_prefix = ""
########################################################################################################################
"""


class DemoTwoSpider(AyuSpider):
    name = "demo_two"
    allowed_domains = ["csdn.net"]
    start_urls = ["https://blog.csdn.net/"]
    custom_settings = {
        # 数据表的前缀名称，用于标记属于哪个项目（也可不配置此参数，按需配置）
        "MONGODB_COLLECTION_PREFIX": "demo2_",
        "ITEM_PIPELINES": {
            # 激活此项则数据会存储至 MongoDB
            "ayugespidertools.Pipelines.AyuFtyMongoPipeline": 300,
        },
        "DOWNLOADER_MIDDLEWARES": {
            # 随机请求头
            "ayugespidertools.Middlewares.RandomRequestUaMiddleware": 400,
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
            # 这里的所有解析规则可选择自己习惯的
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

            # 1. ayugespidertools 推荐的风格写法(更直观)
            article_info = {
                "article_detail_url": DataItem(article_detail_url, "文章详情链接"),
                "article_title": DataItem(article_title, "文章标题"),
                "comment_count": DataItem(comment_count, "文章评论数量"),
                "favor_count": DataItem(favor_count, "文章赞成数量"),
                "nick_name": DataItem(nick_name, "文章作者昵称"),
            }

            """
            # 2.或者这么写，MongoDB 不需要注释参数，这里只有注解的附加功能。但还是推荐使用 DataItem 以
            # 保持风格一致，但也可直接按照下面 4 中的 dict 示例写法
            article_info = {
                "article_detail_url": DataItem(article_detail_url),
                "article_title": DataItem(article_title),
                "comment_count": DataItem(comment_count),
                "favor_count": DataItem(favor_count),
                "nick_name": DataItem(nick_name),
            }
            
            # 3.当然这么写也可以，但是不推荐，写法复杂易错
            article_info = {
                "article_detail_url": {
                    "key_value": article_detail_url,
                    "notes": "文章详情链接",
                },
                "article_title": {
                    "key_value": article_title,
                    "notes": "文章标题",
                },
                "comment_count": {
                    "key_value": comment_count,
                    "notes": "文章评论数量",
                },
                "favor_count": {
                    "key_value": favor_count,
                    "notes": "文章赞成数量",
                },
                "nick_name": {
                    "key_value": nick_name,
                    "notes": "文章作者昵称",
                },
            }
            
            # 4.应该是最简约的示例了
            article_info = {
                "article_detail_url": article_detail_url,
                "article_title": article_title,
                "comment_count": comment_count,
                "favor_count": favor_count,
                "nick_name": nick_name,
            }
            """

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
