# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from ayugespidertools.common.multiplexing import ReuseOperation

try:
    from elasticsearch_dsl import Document, Keyword, Text, connections

    connections.create_connection(hosts="http://localhost:9200")
except ImportError:
    # pip install elasticsearch-dsl
    pass


class ArticleType(Document):
    book_name = Text(analyzer="snowball", fields={"raw": Keyword()})
    book_href = Keyword()
    book_intro = Keyword()

    class Index:
        name = "demo_es"
        settings = {
            "number_of_shards": 2,
        }


class AyuESPipeline:
    def open_spider(self, spider):
        # 这里可以添加是否初始化 es Document 的功能，用于判断是否
        # 创建 es 索引；
        pass

    def process_item(self, item, spider):
        item_dict = ReuseOperation.item_to_dict(item)
        alert_item = ReuseOperation.reshape_item(item_dict)
        es_item = ArticleType(**alert_item.new_item)
        es_item.save()
        return item


if __name__ == "__main__":
    ArticleType.init()
