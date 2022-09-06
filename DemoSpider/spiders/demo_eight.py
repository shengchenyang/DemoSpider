import pandas
from scrapy.http import Request
from DemoSpider.settings import logger
from DemoSpider.common.DataEnum import TableEnum
from ayugespidertools.AyugeSpider import AyuSpider
from ayugespidertools.common.Utils import ToolsForAyu
from ayugespidertools.Items import MysqlDataItem, MongoDataItem


"""
########################################################################################################################
# collection_website: CSDN - 专业开发者社区
# collection_content: 热榜文章排名 Demo 采集示例 - 同时存入 Mysql 和 MongoDB 的场景
# create_time: 2022-08-22
# explain: 根据本项目中的 demo_one 脚本修改而得
# demand_code_prefix = ""
########################################################################################################################
"""


class DemoEightSpider(AyuSpider):
    name = "demo_eight"
    allowed_domains = ["blog.csdn.net"]
    start_urls = ["https://blog.csdn.net/"]

    # 数据库表的枚举信息
    custom_table_enum = TableEnum
    # 初始化配置的类型
    settings_type = "debug"
    custom_settings = {
        # 是否开启记录项目相关运行统计信息
        "RECORD_LOG_TO_MYSQL": False,
        # 数据表的前缀名称，用于标记属于哪个项目，也可以不用添加
        "MYSQL_TABLE_PREFIX": "demo8_",
        # 数据表的前缀名称，用于标记属于哪个项目（也可不配置此参数，按需配置）
        "MONGODB_COLLECTION_PREFIX": "demo8_",
        "ITEM_PIPELINES": {
            # 激活此项则数据会存储至 Mysql
            "ayugespidertools.Pipelines.AyuFtyMysqlPipeline": 300,
            # 激活此项则数据会存储至 MongoDB
            "ayugespidertools.Pipelines.AyuFtyMongoPipeline": 301,
        },
        "DOWNLOADER_MIDDLEWARES": {
            # 随机请求头
            "ayugespidertools.Middlewares.RandomRequestUaMiddleware": 400,
        },
    }

    # 打开 mysql 引擎开关，用于数据入库前更新逻辑判断
    mysql_engine_enabled = True

    def start_requests(self):
        """
        get 请求首页，获取项目列表数据
        """
        yield Request(
            url="https://blog.csdn.net/phoenix/web/blog/hot-rank?page=0&pageSize=25&type=",
            callback=self.parse_first,
            headers={
                "referer": "https://blog.csdn.net/rank/list",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
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

            article_info = {
                "article_detail_url": {
                    "key_value": article_detail_url,
                    "notes": "文章详情链接",
                },
                "article_title": {"key_value": article_title, "notes": "文章标题"},
                "comment_count": {"key_value": comment_count, "notes": "文章评论数量"},
                "favor_count": {"key_value": favor_count, "notes": "文章赞成数量"},
                "nick_name": {"key_value": nick_name, "notes": "文章作者昵称"},
            }

            ArticleMysqlInfoItem = MysqlDataItem(
                alldata=article_info,
                table=TableEnum.article_list_table.value["value"],
            )
            yield ArticleMysqlInfoItem

            ArticleInfoMongoItem = MongoDataItem(
                # alldata 用于存储 mongo 的 Document 文档所需要的字段映射
                alldata=article_info,
                # table 为 mongo 的存储 Collection 集合的名称
                table=TableEnum.article_list_table.value["value"],
                # mongo_update_rule 为查询数据是否存在的规则
                mongo_update_rule={"article_detail_url": article_detail_url},
            )
            yield ArticleInfoMongoItem
