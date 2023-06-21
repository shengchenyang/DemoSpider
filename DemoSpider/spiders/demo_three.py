import json

import pandas
from ayugespidertools.common.utils import ToolsForAyu
from ayugespidertools.items import AyuItem, DataItem
from ayugespidertools.spiders import AyuSpider
from loguru import logger
from scrapy.http import Request

from DemoSpider.items import TableEnum

"""
########################################################################################################################
# collection_website: CSDN - 专业开发者社区
# collection_content: 热榜文章排名 Demo 采集示例 - 存入 Mysql (配置根据 consul 的应用管理中心中取值)
# create_time: 2022-08-07
# explain:
# demand_code_prefix = ""
########################################################################################################################
"""


class DemoThreeSpider(AyuSpider):
    name = "demo_three"
    allowed_domains = ["blog.csdn.net"]
    start_urls = ["https://blog.csdn.net/"]

    # 数据库表的枚举信息
    custom_table_enum = TableEnum
    custom_settings = {
        # 是否开启 consul 的应用管理中心取值的功能(也需要设置 CONSUL_CONF 的值，本示例在 settings 中配置)
        "APP_CONF_MANAGE": True,
        "ITEM_PIPELINES": {
            # 激活此项则数据会存储至 Mysql
            "ayugespidertools.pipelines.AyuFtyMysqlPipeline": 300,
        },
        "DOWNLOADER_MIDDLEWARES": {
            # 随机请求头
            "ayugespidertools.middlewares.RandomRequestUaMiddleware": 400,
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
            },
            dont_filter=True,
        )

    def parse_first(self, response):
        data_list = json.loads(response.text)["data"]
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

            ArticleInfoItem = AyuItem(
                article_detail_url=DataItem(article_detail_url, "文章详情链接"),
                article_title=DataItem(article_title, "文章标题"),
                comment_count=DataItem(comment_count, "文章评论数量"),
                favor_count=DataItem(favor_count, "文章赞成数量"),
                nick_name=DataItem(nick_name, "文章作者昵称"),
                _table=TableEnum.article_list_table.value["value"],
            )
            self.slog.info(f"ArticleInfoItem: {ArticleInfoItem}")
            # yield ArticleInfoItem

            try:
                # 测试 mysql_engine 的功能
                sql = """select `id` from `{}` where `article_detail_url` = "{}" limit 1""".format(
                    TableEnum.article_list_table.value["value"],
                    article_detail_url,
                )
                df = pandas.read_sql(sql, self.mysql_engine)

                # 如果为空，说明此数据不存在于数据库，则新增
                if df.empty:
                    yield ArticleInfoItem

                # 如果已存在，1). 若需要更新，请自定义更新数据结构和更新逻辑；2). 若不用更新，则跳过即可。
                else:
                    logger.debug(f"标题为 ”{article_title}“ 的数据已存在")

            except Exception:
                yield ArticleInfoItem
