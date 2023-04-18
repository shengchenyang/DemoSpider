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

# 这是需要链接的数据库配置，请自行设置
LOCAL_MYSQL_CONFIG = {
    "HOST": config_parser.get("MYSQL", "HOST", fallback=None),
    "PORT": config_parser.getint("MYSQL", "PORT", fallback=3306),
    "USER": config_parser.get("MYSQL", "USER", fallback="root"),
    "PASSWORD": config_parser.get("MYSQL", "PASSWORD", fallback=None),
    "CHARSET": config_parser.get("MYSQL", "CHARSET", fallback="utf8mb4"),
    "DATABASE": config_parser.get("MYSQL", "DATABASE", fallback=None),
    # 数据库 engin 采用的驱动，可不填此参数
    "DRIVER": "mysqlconnector",
}

# 测试 MongoDB 数据库配置
LOCAL_MONGODB_CONFIG = {
    "HOST": config_parser.get("MONGODB", "HOST", fallback=None),
    "PORT": config_parser.getint("MONGODB", "PORT", fallback=27017),
    "AUTHSOURCE": config_parser.get("MONGODB", "AUTHSOURCE", fallback="admin"),
    "USER": config_parser.get("MONGODB", "USER", fallback="admin"),
    "PASSWORD": config_parser.get("MONGODB", "PASSWORD", fallback=None),
    "DATABASE": config_parser.get("MONGODB", "DATABASE", fallback=None),
}

# consul 应用管理的连接配置
CONSUL_CONFIG = {
    "URL": config_parser.get("CONSUL", "URL", fallback=None),
    # 此 token 值只需要只读权限即可，只用于取配置值
    "TOKEN": config_parser.get("CONSUL", "TOKEN", fallback=None),
    "FORMAT": config_parser.get("CONSUL", "FORMAT", fallback="json"),
}

# 动态隧道代理（快代理版本）
DYNAMIC_PROXY_CONFIG = {
    "PROXY_URL": config_parser.get("KDL_DYNAMIC_PROXY", "PROXY_URL", fallback=None),
    "USERNAME": config_parser.get("KDL_DYNAMIC_PROXY", "USERNAME", fallback=None),
    "PASSWORD": config_parser.get("KDL_DYNAMIC_PROXY", "PASSWORD", fallback=None),
}

# 独享代理（快代理版本）
EXCLUSIVE_PROXY_CONFIG = {
    "PROXY_URL": config_parser.get("KDL_EXCLUSIVE_PROXY", "PROXY_URL", fallback=None),
    "USERNAME": config_parser.get("KDL_EXCLUSIVE_PROXY", "USERNAME", fallback=None),
    "PASSWORD": config_parser.get("KDL_EXCLUSIVE_PROXY", "PASSWORD", fallback=None),
    "PROXY_INDEX": config_parser.getint(
        "KDL_EXCLUSIVE_PROXY", "PROXY_INDEX", fallback=1
    ),
}

# ali oss 对象存储
OSS_CONFIG = {
    "OssAccessKeyId": config_parser.get("ALI_OSS", "OssAccessKeyId", fallback=None),
    "OssAccessKeySecret": config_parser.get(
        "ALI_OSS", "OssAccessKeySecret", fallback=None
    ),
    "Endpoint": config_parser.get("ALI_OSS", "Endpoint", fallback=None),
    "examplebucket": config_parser.get("ALI_OSS", "Examplebucket", fallback=None),
    "operateDoc": config_parser.get("ALI_OSS", "OperateDoc", fallback=None),
}

# 日志管理
LOG_FILE = f"{LOG_DIR}/DemoSpider.log"
logger.add(
    env.str("LOG_ERROR_FILE", f"{LOG_DIR}/error.log"),
    level="ERROR",
    rotation="1 week",
    retention="7 days",
    enqueue=True,
)
