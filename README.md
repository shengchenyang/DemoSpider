# AyugeSpiderTools 工具说明

> 本文章用于说明在爬虫开发中遇到的各种通用方法，将其打包成 `Pypi` 包以方便安装和使用，此工具会长久维护。

## 前言
本文是以 `csdn` 的热榜文章为例，来说明此 `scrapy` 扩展的使用方法。

## 1. 前提条件

> `python 3.8+` 可以直接输入以下命令：

```shell
pip install ayugespidertools -i https://pypi.org/simple
```

> 或者自行安装以下依赖：

```ini
python = "^3.8"
opencv-python = "^4.6.0"
numpy = "^1.23.1"
PyExecJS = "^1.5.1"
environs = "^9.5.0"
requests = "^2.28.1"
loguru = "^0.6.0"
Pillow = "^9.2.0"
PyMySQL = "^1.0.2"
Scrapy = "^2.6.2"
pandas = "^1.4.3"
WorkWeixinRobot = "^1.0.1"
crawlab-sdk
pymongo
```

注：若有版本冲突，请去除版本限制即可。

## 2. 使用 ayugespidertools

###  2.1. 导入配置

在项目的 `settings` 中或 `spiders` 的 `custom_setting` 中添加 `LOCAL_MYSQL_CONFIG` 参数

```ini
# 这是需要链接的数据库配置，请自行配置
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
   'MYSQL_CHARSET': 'utf8',
   # 数据库 engin 采用的驱动
   'MYSQL_DRIVER': 'mysqlconnector'
}
```

在 `spiders` 中添加以下所需配置：

```python
# 数据库表的枚举信息
custom_table_enum = Table_Enum
# 配置的类型
settings_type = 'debug'
custom_settings = {
    # 链接的数据库名称，用于返回 mysql_engine 来在 spider 层入库前去重使用
    'MYSQL_DATABASE': "test",
    # 数据表的前缀名称，用于标记属于哪个项目
    'MYSQL_TABLE_PREFIX': "demo_",

    # 激活此项则数据会存储至 Mysql
    'ITEM_PIPELINES': {
        'ayugespidertools.Pipelines.AyuALSMysqlPipeline': 300,
    },

    'DOWNLOADER_MIDDLEWARES': {
        # 动态隧道代理
        # 'scrapy_zst.middlewares.DynamicProxyDownloaderMiddleware': 125,
        # 独享代理
        # 'ayugespidertools.Middlewares.ExclusiveProxyDownloaderMiddleware': 125,

        # 随机请求头
        'ayugespidertools.Middlewares.RandomRequestUaMiddleware': 300,
    },

    # 独享代理配置(激活 DOWNLOADER_MIDDLEWARES 中的独享代理时使用)
    'exclusive_proxy_config': {
        "proxy_url": "独享代理地址：'http://***.com/api/***&num=100&format=json'",
        "username": "独享代理用户名",
        "password": "对应用户的密码",
        "proxy_index": "需要返回的独享代理的索引",
    }
}

# 打开 mysql 引擎开关，用于数据入库前更新逻辑判断
mysql_engine_off = True
```

###  2.2. yield item

在 `yield item` 时，要把需要存储的数据放到 `alldata` 字段中，程序会自动创建 `Table_Enum` 中的所依赖的数据表

```python
Aritle_Info = dict()
Aritle_Info['article_detail_url'] = {'key_value': article_detail_url, 'notes': '文章详情链接'}
Aritle_Info['article_title'] = {'key_value': article_title, 'notes': '文章标题'}
Aritle_Info['comment_count'] = {'key_value': comment_count, 'notes': '文章评论数量'}
Aritle_Info['favor_count'] = {'key_value': favor_count, 'notes': '文章收藏数量'}
Aritle_Info['nick_name'] = {'key_value': nick_name, 'notes': '文章作者昵称'}

AritleInfoItem = DataItem()
AritleInfoItem['alldata'] = Aritle_Info
AritleInfoItem['table'] = Table_Enum.aritle_list_table.value['value']
logger.info(f"AritleInfoItem: {AritleInfoItem}")
```

### 2.3. 去重查询

`mysql_engine` 用于数据入库前的查询使用：

```python
sql = '''select `id` from `{}` where `article_detail_url` = "{}" limit 1'''.format(self.custom_settings['MYSQL_TABLE_PREFIX'] + Table_Enum.aritle_list_table.value['value'], article_detail_url)
df = pandas.read_sql(sql, self.mysql_engine)
```

### 2.4. 中间件及 pipelines 介绍

> 详细说明暂略，请看此项目 `spiders` 中的文件

若要使用具体场景下的 `middlewares` 或 `pipelines` 时，激活它即可。

## 3. 图片示例

如果不存在目标数据库，数据表或表字段，则自动创建项目所依赖的数据库，数据表和表字段。

![image-20220803151448062](http://175.178.210.193:9000/drawingbed/image/image-20220803151448062.png)
