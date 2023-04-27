# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from enum import Enum, unique
from ayugespidertools.common.typevars import TableTemplate

@unique
class TableEnum(Enum):
    """
    数据库表枚举信息示例，用于限制存储信息类的字段及值不允许重复和修改
    """

    article_list_table = TableTemplate(
        value="article_info_list",
        notes="项目列表信息",
        demand_code="DemoSpider_article_list_table_demand_code",
    )

    # 小说列表信息
    book_info_list_table = TableTemplate(
        value="book_info_list",
        notes="小说列表信息",
        demand_code="DemoSpider_book_info_list_table_demand_code",
    )

    # 如果项目中依赖其它表格，请按照上方示例进行增加或修改

class DemospiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
