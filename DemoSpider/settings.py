# Scrapy settings for DemoSpider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import configparser
from os.path import abspath, dirname, join

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
CONFIG_DIR = dirname(abspath(__file__))
# 日志文件存储目录
LOG_DIR = join(CONFIG_DIR, "logs")
# 依赖文件和存储文件的目录
DOC_DIR = join(CONFIG_DIR, "docs")
# 密钥配置等信息存储目录
VIT_DIR = join(CONFIG_DIR, "VIT")

# 加载秘钥等配置信息
config_parser = configparser.ConfigParser()
config_parser.read(f"{VIT_DIR}/.conf", encoding="utf-8")

# 这是需要链接的数据库配置，请自行设置
if mysql_ini_exists := config_parser.has_section("MYSQL"):
    mysql_ini = config_parser["MYSQL"]
    LOCAL_MYSQL_CONFIG = {
        "HOST": mysql_ini.get("HOST"),
        "PORT": mysql_ini.getint("PORT", 3306),
        "USER": mysql_ini.get("USER", "root"),
        "PASSWORD": mysql_ini.get("PASSWORD"),
        "CHARSET": mysql_ini.get("CHARSET", "utf8mb4"),
        "DATABASE": mysql_ini.get("DATABASE"),
        # 数据库 engin 采用的驱动，可不填此参数
        "DRIVER": "mysqlconnector",
    }

# 测试 MongoDB 数据库配置
if mongodb_ini_exists := config_parser.has_section("MONGODB"):
    mongodb_ini = config_parser["MONGODB"]
    LOCAL_MONGODB_CONFIG = {
        "HOST": mongodb_ini.get("HOST"),
        "PORT": mongodb_ini.getint("PORT", 27017),
        "AUTHSOURCE": mongodb_ini.get("AUTHSOURCE"),
        "USER": mongodb_ini.get("USER", "admin"),
        "PASSWORD": mongodb_ini.get("PASSWORD"),
        "DATABASE": mongodb_ini.get("DATABASE"),
    }

# consul 应用管理的连接配置
if consul_ini_exists := config_parser.has_section("CONSUL"):
    consul_ini = config_parser["CONSUL"]
    CONSUL_CONFIG = {
        "HOST": consul_ini["HOST"],
        "PORT": consul_ini["PORT"],
        # 此 token 值只需要只读权限即可，只用于取配置值
        "TOKEN": consul_ini["TOKEN"],
        # 这个是应用管理中心最终的 key 值，如果不设置此值会默认设置值为中程序中的 ENV 值
        "KEY_VALUES": consul_ini["KEY_VALUES"],
        # 这个是此配置在应用管理中心所属的 group，默认为空(按需配置，如果不需要直接不配置此值或配置为空皆可)
        "GROUP": consul_ini["GROUP"],
    }

# 动态隧道代理（快代理版本）
if kdl_dynamic_proxy_ini_exists := config_parser.has_section("KDL_DYNAMIC_PROXY"):
    kdl_dynamic_proxy_ini = config_parser["KDL_DYNAMIC_PROXY"]
    DYNAMIC_PROXY_CONFIG = {
        "PROXY_URL": kdl_dynamic_proxy_ini["PROXY_URL"],
        "USERNAME": kdl_dynamic_proxy_ini["USERNAME"],
        "PASSWORD": kdl_dynamic_proxy_ini["PASSWORD"],
    }

# 独享代理（快代理版本）
if kdl_exclusive_proxy_ini_exists := config_parser.has_section("KDL_EXCLUSIVE_PROXY"):
    kdl_exclusive_proxy_ini = config_parser["KDL_EXCLUSIVE_PROXY"]
    EXCLUSIVE_PROXY_CONFIG = {
        "PROXY_URL": kdl_exclusive_proxy_ini["PROXY_URL"],
        "USERNAME": kdl_exclusive_proxy_ini["USERNAME"],
        "PASSWORD": kdl_exclusive_proxy_ini["PASSWORD"],
        "PROXY_INDEX": kdl_exclusive_proxy_ini["PROXY_INDEX"],
    }

# ali oss 对象存储
if ali_oss_ini_exists := config_parser.has_section("ALI_OSS"):
    ali_oss_ini = config_parser["ALI_OSS"]
    OSS_CONFIG = {
        "OssAccessKeyId": ali_oss_ini["OssAccessKeyId"],
        "OssAccessKeySecret": ali_oss_ini["OssAccessKeySecret"],
        "Endpoint": ali_oss_ini["Endpoint"],
        "examplebucket": ali_oss_ini["Examplebucket"],
        "operateDoc": ali_oss_ini["OperateDoc"],
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
