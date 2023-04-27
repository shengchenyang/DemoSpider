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

from environs import Env
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

env = Env()
env.read_env()

# 项目根目录
CONFIG_DIR = Path(__file__).parent
# 日志文件存储目录
LOG_DIR = CONFIG_DIR / "logs"
# 依赖文件和存储文件的目录
DOC_DIR = CONFIG_DIR / "docs"
# 密钥配置等信息存储目录
VIT_DIR = CONFIG_DIR / "VIT"

# 加载秘钥等配置信息
config_parser = configparser.ConfigParser()
config_parser.read(f"{VIT_DIR}/.conf", encoding="utf-8")

# Mysql 数据库配置
LOCAL_MYSQL_CONFIG = {
    "host": config_parser.get("mysql", "host", fallback=None),
    "port": config_parser.getint("mysql", "port", fallback=3306),
    "user": config_parser.get("mysql", "user", fallback="root"),
    "password": config_parser.get("mysql", "password", fallback=None),
    "charset": config_parser.get("mysql", "charset", fallback="utf8mb4"),
    "database": config_parser.get("mysql", "database", fallback=None),
    # 数据库 engin 采用的驱动，可不填此参数
    "driver": "mysqlconnector",
}

# MongoDB 数据库配置
LOCAL_MONGODB_CONFIG = {
    "host": config_parser.get("mongodb", "host", fallback=None),
    "port": config_parser.getint("mongodb", "port", fallback=27017),
    "authsource": config_parser.get("mongodb", "authsource", fallback="admin"),
    "user": config_parser.get("mongodb", "user", fallback="admin"),
    "password": config_parser.get("mongodb", "password", fallback=None),
    "database": config_parser.get("mongodb", "database", fallback=None),
}

# consul 应用管理的连接配置
CONSUL_CONFIG = {
    "token": config_parser.get("consul", "token", fallback=None),
    "url": config_parser.get("consul", "url", fallback=None),
    "format": config_parser.get("consul", "format", fallback="json"),
}

# 动态隧道代理（快代理版本）
DYNAMIC_PROXY_CONFIG = {
    "proxy": config_parser.get("kdl_dynamic_proxy", "proxy", fallback=None),
    "username": config_parser.get("kdl_dynamic_proxy", "username", fallback=None),
    "password": config_parser.get("kdl_dynamic_proxy", "password", fallback=None),
}

# 独享代理（快代理版本）
EXCLUSIVE_PROXY_CONFIG = {
    "proxy": config_parser.get("kdl_exclusive_proxy", "proxy", fallback=None),
    "username": config_parser.get("kdl_exclusive_proxy", "username", fallback=None),
    "password": config_parser.get("kdl_exclusive_proxy", "password", fallback=None),
    "index": config_parser.getint(
        "kdl_exclusive_proxy", "index", fallback=1
    ),
}

# ali oss 对象存储
OSS_CONFIG = {
    "accesskeyid": config_parser.get("ali_oss", "accesskeyid", fallback=None),
    "accesskeysecret": config_parser.get(
        "ali_oss", "accesskeysecret", fallback=None
    ),
    "endpoint": config_parser.get("ali_oss", "endpoint", fallback=None),
    "bucket": config_parser.get("ali_oss", "bucket", fallback=None),
    "doc": config_parser.get("ali_oss", "doc", fallback=None),
}

# 日志管理
LOG_LEVEL = env.str("LOG_LEVEL", "ERROR")
LOG_FILE = f"{LOG_DIR}/DemoSpider.log"
logger.add(
    env.str("LOG_ERROR_FILE", f"{LOG_DIR}/error.log"),
    level="ERROR",
    rotation="1 week",
    retention="7 days",
    enqueue=True,
)
