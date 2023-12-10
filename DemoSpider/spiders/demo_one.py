# 热榜文章排名 Demo 采集示例 - 存入 Mysql (配置根据本地 .conf 取值)
import json
from typing import Union

from ayugespidertools.common.utils import ToolsForAyu
from ayugespidertools.items import AyuItem, DataItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request
from scrapy.http.response.html import HtmlResponse
from scrapy.http.response.text import TextResponse
from sqlalchemy import text


class DemoOneSpider(AyuSpider):
    name = "demo_one"
    allowed_domains = ["blog.csdn.net"]
    start_urls = ["https://blog.csdn.net/"]
    custom_settings = {
        # 打开数据库引擎开关，用于数据入库前更新逻辑判断
        "DATABASE_ENGINE_ENABLED": True,
        "ITEM_PIPELINES": {
            # 激活此项则数据会存储至 Mysql
            "ayugespidertools.pipelines.AyuFtyMysqlPipeline": 300,
            # 激活此项则会记录脚本运行情况
            # "ayugespidertools.pipelines.AyuStatisticsMysqlPipeline": 301,
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

    def parse_first(self, response: Union[HtmlResponse, TextResponse]):
        data_list = json.loads(response.text)["data"]
        for curr_data in data_list:
            # 这里的所有解析方式可选择自己习惯的其它任意库，xpath， json 或正则等等。
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

            _save_table = "demo_one"
            # 数据存储方式 1，需要添加注释时的写法
            ArticleInfoItem = AyuItem(
                # 这里也可以写为 article_detail_url = DataItem(article_detail_url)，但没有注释
                # 功能了，那不如使用下面的数据存储方式 2
                article_detail_url=DataItem(article_detail_url, "文章详情链接"),
                article_title=DataItem(article_title, "文章标题"),
                comment_count=DataItem(comment_count, "文章评论数量"),
                favor_count=DataItem(favor_count, "文章赞成数量"),
                nick_name=DataItem(nick_name, "文章作者昵称"),
                _table=DataItem(_save_table, "项目列表信息"),
            )

            # 数据存储方式 2，若不需要注释，也可以这样写，但不要两种风格混用
            """
            ArticleInfoItem = AyuItem(
                article_detail_url=article_detail_url,
                article_title=article_title,
                comment_count=comment_count,
                favor_count=favor_count,
                nick_name=nick_name,
                _table=_save_table,
            )
            """

            # 数据存储方式 3，当然也可以直接 yield dict
            # 但 _table，_mongo_update_rule 等参数就没有 IDE 提示功能了
            """
            yield {
                "article_detail_url": article_detail_url,
                "article_title": article_title,
                "comment_count": comment_count,
                "favor_count": favor_count,
                "nick_name": nick_name,
                "_table": _save_table,
            }
            """

            self.slog.info(f"ArticleInfoItem: {ArticleInfoItem}")
            # yield ArticleInfoItem

            if self.mysql_engine_conn:
                try:
                    _sql = text(
                        f"""select `id` from `{_save_table}` where `article_detail_url` = "{article_detail_url}" limit 1"""
                    )
                    result = self.mysql_engine_conn.execute(_sql).fetchone()
                    if not result:
                        self.mysql_engine_conn.rollback()
                        yield ArticleInfoItem
                    else:
                        self.slog.debug(f'标题为 "{article_title}" 的数据已存在')
                except Exception:
                    self.mysql_engine_conn.rollback()
                    yield ArticleInfoItem
            else:
                yield ArticleInfoItem

            # 使用 pandas 结合对应 <db>_engine 去重的示例：
            """
            import pandas
            try:
                sql = f'''select `id` from `{_save_table}` where `article_detail_url` = "{article_detail_url}" limit 1'''
                df = pandas.read_sql(sql, self.mysql_engine)

                # 如果为空，说明此数据不存在于数据库，则新增
                if df.empty:
                    yield ArticleInfoItem

                # 如果已存在，1). 若需要更新，请自定义更新数据结构和更新逻辑；2). 若不用更新，则跳过即可。
                else:
                    self.slog.debug(f"标题为 ”{article_title}“ 的数据已存在")

            except Exception as e:
                if any(["1146" in str(e), "1054" in str(e), "doesn't exist" in str(e)]):
                    yield ArticleInfoItem
                else:
                    self.slog.error(f"请查看数据库链接或网络是否通畅！Error: {e}")
            """
