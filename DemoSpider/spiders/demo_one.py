import json
from scrapy.http import Request
from DemoSpider.settings import logger
from ayugespidertools.Items import MysqlDataItem
from DemoSpider.common.DataEnum import TableEnum
from ayugespidertools.AyugeSpider import AyuSpider
from ayugespidertools.common.Utils import ToolsForAyu


"""
########################################################################################################################
# collection_website: CSDN - 专业开发者社区
# collection_content: 热榜文章排名 Demo 采集示例 - 存入 Mysql (配置根据本地 settings 的 LOCAL_MYSQL_CONFIG 中取值)
# create_time: 2022-07-30
# explain:
# demand_code_prefix = ""
########################################################################################################################
"""


class DemoOneSpider(AyuSpider):
    name = "demo_one"
    allowed_domains = ["blog.csdn.net"]
    start_urls = ["https://blog.csdn.net/"]

    # 数据库表的枚举信息
    custom_table_enum = TableEnum
    # 初始化配置的类型
    settings_type = "debug"
    custom_settings = {
        # scrapy 日志等级配置
        "LOG_LEVEL": "DEBUG",
        # 是否开启记录项目相关运行统计信息。不配置默认为 False
        "RECORD_LOG_TO_MYSQL": False,
        # 设置 ayugespidertools 库的日志输出为 loguru，可自行配置 logger 规则来管理项目日志。若不配置此项，库日志只会在控制台上打印
        "LOGURU_CONFIG": logger,
        # Mysql数据表的前缀名称，用于标记属于哪个项目，也可以不用配置
        "MYSQL_TABLE_PREFIX": "demo1_",
        "ITEM_PIPELINES": {
            # 激活此项则数据会存储至 Mysql
            "ayugespidertools.Pipelines.AyuFtyMysqlPipeline": 300,
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

            # 数据存储方式1，非常推荐此写法。article_info 含有所有需要存储至表中的字段
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

            """
            # 当然这么写也可以，但是不推荐
            article_info = {
                "article_detail_url": article_detail_url,
                "article_title": article_title,
                "comment_count": comment_count,
                "favor_count": favor_count,
                "nick_name": nick_name,
            }
            """

            ArticleInfoItem = MysqlDataItem(
                alldata=article_info,
                table=TableEnum.article_list_table.value["value"],
            )

            self.slog.info(f"ArticleInfoItem: {ArticleInfoItem}")

            """
            # 旧 scrapy 脚本也可方便地改写为 ayugespidertools 支持的示例
            # 也可以不用修改，只需补充上所需要的 table 和 item_mode 字段，来指定存储表名和存储方式
            item = dict()
            item["article_detail_url"] = article_detail_url
            item["article_title"] = article_title
            item["comment_count"] = comment_count
            item["favor_count"] = favor_count
            item["nick_name"] = nick_name

            item["table"] = "article_info_list"
            item["item_mode"] = "Mysql"
            yield item

            # 或者这样写
            item = {
                "article_detail_url": article_detail_url,
                "article_title": article_title,
                "comment_count": comment_count,
                "favor_count": favor_count,
                "nick_name": nick_name,
                # 兼容旧写法，但是要添加 table 字段和 item_mode 字段
                # (即需要存储的表格名称，注意：是去除表格前缀的表名, 比如表为 demo_article_info_list，前缀为 demo_，则 table 名为 article_info_list)
                "table": "article_info_list",
                "item_mode": "Mysql",
            }
            yield item
            """

            # 数据入库逻辑 -> 测试 mysql_engine 的去重功能
            sql = """select `id` from `{}` where `article_detail_url` = "{}" limit 1""".format(
                self.custom_settings.get("MYSQL_TABLE_PREFIX", "")
                + TableEnum.article_list_table.value["value"],
                article_detail_url,
            )
            yield ToolsForAyu.filter_data_before_yield(
                sql=sql,
                mysql_engine=self.mysql_engine,
                item=ArticleInfoItem,
            )
