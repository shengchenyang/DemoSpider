# 热榜文章排名 Demo 采集示例 - 存入 Mysql (配置根据 consul 取值)
import json

from ayugespidertools.common.utils import ToolsForAyu
from ayugespidertools.items import AyuItem, DataItem
from ayugespidertools.spiders import AyuSpider
from loguru import logger
from scrapy.http import Request
from sqlalchemy import text


class DemoThreeSpider(AyuSpider):
    name = "demo_three"
    allowed_domains = ["blog.csdn.net"]
    start_urls = ["https://blog.csdn.net/"]
    custom_settings = {
        # 打开 mysql 引擎开关，用于数据入库前更新逻辑判断
        "MYSQL_ENGINE_ENABLED": True,
        # 开启远程配置服务(优先级 consul > nacos)
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

            _save_table = "demo_three"
            ArticleInfoItem = AyuItem(
                article_detail_url=DataItem(article_detail_url, "文章详情链接"),
                article_title=DataItem(article_title, "文章标题"),
                comment_count=DataItem(comment_count, "文章评论数量"),
                favor_count=DataItem(favor_count, "文章赞成数量"),
                nick_name=DataItem(nick_name, "文章作者昵称"),
                _table=DataItem(_save_table, "项目列表信息"),
            )
            self.slog.info(f"ArticleInfoItem: {ArticleInfoItem}")
            # yield ArticleInfoItem

            try:
                _sql = text(
                    f"""select `id` from `{_save_table}` where `article_detail_url` = "{article_detail_url}" limit 1"""
                )
                result = self.mysql_engine.execute(_sql).fetchone()
                if not result:
                    yield ArticleInfoItem
                else:
                    self.slog.debug(f'标题为 "{article_title}" 的数据已存在')
            except Exception as e:
                # 若数据库或数据表不存在时，直接返回 item 即可，会自动创建所依赖的数据库数据表及字段注释（前提是用户有对应权限）
                if any(["1146" in str(e), "1054" in str(e), "doesn't exist" in str(e)]):
                    yield ArticleInfoItem
                else:
                    raise ValueError(f"请查看网络是否通畅，或 sql 是否正确！Error: {e}") from e
