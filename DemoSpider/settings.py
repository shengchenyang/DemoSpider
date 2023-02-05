import configparser
from environs import Env
from loguru import logger
from os.path import dirname, abspath, join


BOT_NAME = "DemoSpider"

SPIDER_MODULES = ["DemoSpider.spiders"]
NEWSPIDER_MODULE = "DemoSpider.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"

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
config_parse = configparser.ConfigParser()
config_parse.read(f"{VIT_DIR}/.conf", encoding="utf-8")

# 这是需要链接的数据库配置，请自行设置
mysql_ini = config_parse["MYSQL"]
LOCAL_MYSQL_CONFIG = {
    # 数据库IP
    "HOST": mysql_ini["HOST"],
    # 数据库端口
    "PORT": int(mysql_ini["PORT"]),
    # 数据库用户名
    "USER": mysql_ini["USER"],
    # 数据库密码
    "PASSWORD": mysql_ini["PASSWORD"],
    # 数据库编码
    "CHARSET": mysql_ini["CHARSET"],
    # 数据库 engin 采用的驱动，可不填此参数
    "DRIVER": "mysqlconnector",
    # 数据库
    "DATABASE": mysql_ini["DATABASE"],
}

# 测试 MongoDB 数据库配置
mongodb_ini = config_parse["MONGODB"]
LOCAL_MONGODB_CONFIG = {
    "HOST": mongodb_ini["HOST"],
    "PORT": int(mongodb_ini["PORT"]),
    "AUTHSOURCE": mongodb_ini["AUTHSOURCE"],
    "USER": mongodb_ini["USER"],
    "PASSWORD": mongodb_ini["PASSWORD"],
    "DATABASE": mongodb_ini["DATABASE"],
}

# scrapy Request 替换为 aiohttp 的配置
LOCAL_AIOHTTP_CONFIG = {
    "TIMEOUT": 5,
    "PROXY": "127.0.0.1:1080",
    "SLEEP": 0,
    "RETRY_TIMES": 3,
}

# consul 应用管理的连接配置
consul_ini = config_parse["CONSUL"]
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
kdl_dynamic_proxy_ini = config_parse["KDL_DYNAMIC_PROXY"]
DYNAMIC_PROXY_CONFIG = {
    "PROXY_URL": kdl_dynamic_proxy_ini["PROXY_URL"],
    "USERNAME": kdl_dynamic_proxy_ini["USERNAME"],
    "PASSWORD": kdl_dynamic_proxy_ini["PASSWORD"],
}

# 独享代理（快代理版本）
kdl_exclusive_proxy_ini = config_parse["KDL_EXCLUSIVE_PROXY"]
EXCLUSIVE_PROXY_CONFIG = {
    "PROXY_URL": kdl_exclusive_proxy_ini["PROXY_URL"],
    "USERNAME": kdl_exclusive_proxy_ini["USERNAME"],
    "PASSWORD": kdl_exclusive_proxy_ini["PASSWORD"],
    "PROXY_INDEX": kdl_exclusive_proxy_ini["PROXY_INDEX"],
}

# ali oss 对象存储
ali_oss_ini = config_parse["ALI_OSS"]
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
