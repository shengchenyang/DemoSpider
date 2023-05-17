# Scrapy settings for DemoSpider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import configparser
from pathlib import Path

from loguru import logger

BOT_NAME = "DemoSpider"

SPIDER_MODULES = ["DemoSpider.spiders"]
NEWSPIDER_MODULE = "DemoSpider.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"


# 项目根目录
CONFIG_DIR = Path(__file__).parent
# 日志文件存储目录
LOG_DIR = CONFIG_DIR / "logs"
# 依赖文件和存储文件的目录
DOC_DIR = CONFIG_DIR / "docs"
# 密钥配置等信息存储目录
VIT_DIR = CONFIG_DIR / "VIT"

# 日志管理
LOG_LEVEL = "ERROR"
LOG_FILE = f"{LOG_DIR}/DemoSpider.log"
logger.add(
    f"{LOG_DIR}/error.log",
    level="ERROR",
    rotation="1 week",
    retention="7 days",
    enqueue=True,
)
