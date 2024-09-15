# Scrapy settings for DemoSpider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from pathlib import Path

from loguru import logger

try:
    from ayugespidertools.config import get_cfg
except ImportError:
    # 目前是预发布功能，所以暂时添加 try catch，正常是不需要的。若你安装了预发布版本也是不用的；
    get_cfg = None

BOT_NAME = "DemoSpider"

SPIDER_MODULES = ["DemoSpider.spiders"]
NEWSPIDER_MODULE = "DemoSpider.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Set settings whose default value is deprecated to a future-proof value
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# Set .conf file path. Same as library default, commentable
_ = Path(__file__).parent
VIT_DIR = _ / "VIT"

"""
正常情况下这里任何条件判断都不用写，只要 .conf 中确实配置了对应的参数，直接赋值即可；
这里是因为对预发布功能测试使用，且为了不影响旧项目运行；
一般直接写成 redis_host = _my_cfg["my_add_redis"].get("host", "localhost") 这样即可获
取 .conf 中自定义配置，简洁优雅；
对应的测试请在 spiders/demo_conf.py 中查看。
"""
if get_cfg:
    _my_cfg = get_cfg()
    if _my_cfg.has_section("my_add_redis"):
        redis_host = _my_cfg["my_add_redis"].get("host", "localhost")
        redis_port = _my_cfg["my_add_redis"].getint("port", 6379)
        redis_password = _my_cfg["my_add_redis"].get("password", None)

# Log configuration example
LOG_LEVEL = "ERROR"
LOG_FILE = _ / "logs/DemoSpider.log"
logger.add(
    _ / "logs/error.log",
    level="ERROR",
    rotation="1 week",
    retention="7 days",
    enqueue=True,
)
