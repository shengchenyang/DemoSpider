# Scrapy settings for DemoSpider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'DemoSpider'

SPIDER_MODULES = ['DemoSpider.spiders']
NEWSPIDER_MODULE = 'DemoSpider.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'DemoSpider (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'DemoSpider.middlewares.DemospiderSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'DemoSpider.middlewares.DemospiderDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'DemoSpider.pipelines.DemospiderPipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

import configparser
from environs import Env
from loguru import logger
from os.path import dirname, abspath, join


# 加载秘钥等配置信息
config_parse = configparser.ConfigParser()
config_parse.read("VIT/.conf", encoding="utf-8")


# 这是需要链接的数据库配置，请自行设置
LOCAL_MYSQL_CONFIG = {
   # 数据库IP
   'HOST': config_parse["DEV_MYSQL"]["HOST"],
   # 数据库端口
   'PORT': int(config_parse["DEV_MYSQL"]["PORT"]),
   # 数据库用户名
   'USER': config_parse["DEV_MYSQL"]["USER"],
   # 数据库密码
   'PASSWORD': config_parse["DEV_MYSQL"]["PWD"],
   # 数据库编码
   'MYSQL_CHARSET': 'utf8mb4',
   # 数据库 engin 采用的驱动
   'MYSQL_DRIVER': 'mysqlconnector',
   # 数据库
   'DATABASE': 'test'
}

# 测试 MongoDB 数据库配置
MONGODB_CONFIG = {
  "host": config_parse["DEV_MONGODB"]["HOST"],
  "port": int(config_parse["DEV_MONGODB"]["PORT"]),
  "user": config_parse["DEV_MONGODB"]["USER"],
  "pwd": config_parse["DEV_MONGODB"]["PWD"],
  "database": config_parse["DEV_MONGODB"]["DATABASE"],
}

# 以下是日志配置
env = Env()
env.read_env()

# 项目根目录
CONFIG_DIR = dirname(abspath(__file__))
LOG_DIR = join(CONFIG_DIR, "logs")
# 日志管理
logger.add(env.str("LOG_RUNTIME_FILE", f"{LOG_DIR}/runtime.log"), level="DEBUG", rotation="1 week", retention="7 days")
logger.add(env.str("LOG_ERROR_FILE", f"{LOG_DIR}/error.log"), level="ERROR", rotation="1 week", retention="7 days")
