# Scrapy settings for DemoSpider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from pathlib import Path

from ayugespidertools.config import get_cfg, logger

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

# Get custom configuration from .conf
"""
这里是在 VIT_DIR .conf 中获取自定义配置，用于隐藏隐私数据和统一配置管理；除了在 settings.py 中获取这
些配置，当然也可以直接在对应的 spider 中结合 custom_settings 使用。
"""
_my_cfg = get_cfg()
redis_host = _my_cfg["my_add_redis"].get("host", "localhost")
redis_port = _my_cfg["my_add_redis"].getint("port", 6379)
redis_password = _my_cfg["my_add_redis"].get("password", None)

# Log configuration example
LOG_LEVEL = "ERROR"
LOG_FILE = _ / "logs/DemoSpider.log"
logger.remove()
logger.add(
    _ / "logs/error.log",
    level="ERROR",
    rotation="1 week",
    retention="7 days",
    enqueue=True,
)
