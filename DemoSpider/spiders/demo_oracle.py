# oracle 场景不会添加自动创建数据库，表及字段等功能，请手动管理
from ayugespidertools.common.utils import ToolsForAyu
from ayugespidertools.items import AyuItem, DataItem
from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request
from scrapy.http.response.text import TextResponse
from sqlalchemy import text


class DemoOracleSpider(AyuSpider):
    name = "demo_oracle"
    allowed_domains = ["blog.csdn.net"]
    start_urls = ["https://blog.csdn.net/"]
    custom_settings = {
        "DATABASE_ENGINE_ENABLED": True,
        "ITEM_PIPELINES": {
            "ayugespidertools.pipelines.AyuFtyOraclePipeline": 300,
        },
    }

    def start_requests(self):
        """请求首页，获取项目列表数据"""
        yield Request(
            url="https://blog.csdn.net/phoenix/web/blog/hot-rank?page=0&pageSize=25&type=",
            callback=self.parse_first,
            headers={
                "referer": "https://blog.csdn.net/rank/list",
            },
            cb_kwargs={
                "curr_site": "csdn",
            },
            dont_filter=True,
        )

    def parse_first(self, response: TextResponse, curr_site: str):
        self.slog.info(f"当前采集的站点为: {curr_site}")

        # 可自定义解析规则
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

            _save_table = "_article_info_list"
            ArticleInfoItem = AyuItem(
                article_detail_url=DataItem(article_detail_url, "文章详情链接"),
                article_title=DataItem(article_title, "文章标题"),
                comment_count=DataItem(comment_count, "文章评论数量"),
                favor_count=DataItem(favor_count, "文章赞成数量"),
                nick_name=DataItem(nick_name, "文章作者昵称"),
                _table=DataItem(_save_table, "文章信息列表"),
            )
            self.slog.info(f"ArticleInfoItem: {ArticleInfoItem}")
            # yield ArticleInfoItem

            if self.oracle_engine_conn:
                _sql = text(
                    f"""select 1 from "{_save_table}" where "article_detail_url" = '{article_detail_url}' AND ROWNUM <= 1"""
                )
                result = self.oracle_engine_conn.execute(_sql).fetchone()
                if not result:
                    yield ArticleInfoItem
                else:
                    self.slog.debug(f'标题为 "{article_title}" 的数据已存在')
