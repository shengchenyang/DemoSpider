"""
结合 scrapy-redis 的方式示例：
Note:
    1. 为了方便展示和不干扰 DemoSpider 主项目 settings 的内容，所以将 scrapy-redis 相关
    配置放入了此 spider 的 custom_settings 中了。放入 settings.py 也是可以的。
    2. 运行此示例需要自行配置 custom_settings 中的 REDIS_HOST 和 REDIS_PARAMS 配置，也
    可以修改为 REDIS_URL 的方式。
    3. 其它配置不再展示，具体请查看 scrapy_redis 文档。
    4. 运行方式：执行此 spider，然后在 redis 中执行 lpush myspider:start_urls <start url> 即可。

Supplement:
    1. 需要自行安装 scrapy-redis，且版本要大于等于 v0.8.0。
"""

from typing import Any

from ayugespidertools.items import AyuItem
from ayugespidertools.spiders import AyuSpider

from DemoSpider.common.types import ScrapyResponse

try:
    from scrapy_redis.spiders import RedisSpider
except ImportError:
    # pip install scrapy-redis
    from DemoSpider.common.types import RedisSpider


class MyspiderRedisSpider(AyuSpider, RedisSpider):
    """Spider that reads urls from redis queue (myspider:start_urls)."""

    name = "myspider_redis"
    redis_key = "myspider:start_urls"
    custom_settings = {
        "USER_AGENT": "scrapy-redis (+https://github.com/rolando/scrapy-redis)",
        "DUPEFILTER_CLASS": "scrapy_redis.dupefilter.RFPDupeFilter",
        "SCHEDULER": "scrapy_redis.scheduler.Scheduler",
        "SCHEDULER_PERSIST": True,
        # "SCHEDULER_QUEUE_CLASS": "scrapy_redis.queue.SpiderPriorityQueue",
        # "SCHEDULER_QUEUE_CLASS": "scrapy_redis.queue.SpiderQueue",
        # "SCHEDULER_QUEUE_CLASS": "scrapy_redis.queue.SpiderStack",
        "REDIS_HOST": "***",
        "REDIS_PORT": 6379,
        "REDIS_PARAMS": {"password": "***", "db": 8},
        "ITEM_PIPELINES": {
            # "ayugespidertools.pipelines.AyuFtyMysqlPipeline": 300,
            "scrapy_redis.pipelines.RedisPipeline": 400,
        },
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Dynamically define the allowed domains list.
        domain = kwargs.pop("domain", "")
        self.allowed_domains = filter(None, domain.split(","))
        super(MyspiderRedisSpider, self).__init__(*args, **kwargs)

    def parse(self, response: ScrapyResponse, **kwargs: Any) -> Any:
        """
        # 若不需要 ayugespidertools 的 pipelines 功能，那么直接 yield dict 的方式更好，且
        # 这种场景不需要 _table 参数，比如:
        yield {
            "name": response.css("title::text").get(),
            "url": response.url,
        }
        """
        yield AyuItem(
            name=response.css("title::text").get(),
            url=response.url,
            _table="demo_scrapy_redis",
        ).asdict()
