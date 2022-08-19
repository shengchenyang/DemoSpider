# DemoSpdier 项目说明

## —— 之 AyugeSpiderTools 工具应用示例

> 本文章用于说明 `ayugespidertools` 的 `scrapy` 扩展库在 `python` 爬虫开发中的简单应用，可以**解放爬虫开发人员的双手**：不用关注 `item`, `middlewares` 和 `pipelines` 的编写，专心反爬和 `spiders` 的解析规则即可。

## 前言
本文是以 `csdn` 的热榜文章和纵横小说网为例，来说明此 `scrapy` 扩展库的使用方法。

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
crawlab-sdk = “^0.6.0”
# pymongo 版本要在 3.11.0 及以下
pymongo = "3.11.0"
pytest == “6.2.5”
retrying = “^1.3.3”
SQLAlchemy = "^1.4.39"
DBUtils = "^3.0.2"
```

注：`pymongo` 版本要在 `3.11.0` 及以下的要求是因为我的 mongoDB 的版本为 `3.4`；若依赖库中的库有版本冲突，请去除版本限制即可。

### 1.1. 运行方法

> 本扩展库用于方便 `python` 开发，本项目的应用场景的运行方法为：

只需要将本项目中的 `VIT` 文件夹下的 `.conf` 文件如下编辑，然后 `scrapy crawl xxxx` 对应的 `spiders` 脚本即可。

> `VIT` 文件夹中的 `.conf` 文件内容为，已脱敏，请自行配置：

```ini
[DEV_MYSQL]
HOST=***
PORT=3306
USER=root
PASSWORD=***
DATABASE=***
CHARSET=utf8mb4

[DEV_MONGODB]
HOST=***
PORT=27017
DATABASE=***
AUTHSOURCE=***
USER=***
PASSWORD=***

[DEV_CONSUL]
HOST=***
PORT=***
TOKEN=***
KEY_VALUES=***
GROUP=
```

注：具体请根据 `DemoSpider` 项目中的 `settings` 中的配置来设置

> 项目中各 `spiders` 脚本的功能介绍，如下：

```diff
# 采集数据存入 `Mysql` 的场景：
- 1).demo_one: 配置根据本地 `settings` 的 `LOCAL_MYSQL_CONFIG` 中取值
	5).demo_five: 异步存入 `Mysql` 的场景
+ 3).demo_three: 配置根据 `consul` 的应用管理中心中取值

# 采集数据存入 `MongoDB` 的场景：
- 2).demo_two: 采集数据存入 `MongoDB` 的场景（配置根据本地 `settings` 的 `LOCAL_MONGODB_CONFIG` 中取值）
	6).demo_six: 异步存入 `MongoDB` 的场景
+ 4).demo_four: 采集数据存入 `MongoDB` 的场景（配置根据 `consul` 的应用管理中心中取值）

# 将 Scrapy 的 Request，FormRequest 替换为其它工具实现的场景
- 使用 scrapy 请求的场景
+ 7).demo_seven: 替换为 requests 请求的场景
```


注：其实存入 `Mysql` 和存入 `MongoDB` 的功能可以写在一块，可同时生效，配置不同优先级即可。分开写只是为了方便查看而已。

## 2. 使用 ayugespidertools

以下只对 `demo_one` 的 `spiders` 的脚本进行说明，因为只要你懂得 `Scrapy` 框架，那么项目中的配置对你来说极易上手。而且项目中的代码注释也较详细，并不难理解。

###  2.1. 导入配置

> 在项目的 `settings` 中或 `spiders` 的 `custom_setting` 中添加 `LOCAL_MYSQL_CONFIG` 参数

`demo_one`: `mysql` 场景下的 `settings` 文件中，如下编写：

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
   'PASSWORD': config_parse["DEV_MYSQL"]["PASSWORD"],
   # 数据库编码
   'CHARSET': 'utf8mb4',
   # 数据库
   'DATABASE': 'test'
}
```
注：其实这个配置写在 `custom_settings` 中等地方也是可以的，只是这些配置一般是全局配置，放在 `settings` 中比较好管理而已。

> 在 `spiders` 中添加以下所需配置：

`demo_one`: `mysql` 场景下的 `spiders` 脚本 `demo_one` 文件中，如下编写：

```ini
# 数据库表的枚举信息
custom_table_enum = Table_Enum
# 初始化配置的类型
settings_type = 'debug'
custom_settings = {
    # 数据表的前缀名称，用于标记属于哪个项目
    'MYSQL_TABLE_PREFIX': "demo_",
    'ITEM_PIPELINES': {
        # 激活此项则数据会存储至 Mysql
        'ayugespidertools.Pipelines.AyuFtyMysqlPipeline': 300,
    },
    'DOWNLOADER_MIDDLEWARES': {
        # 随机请求头
        'ayugespidertools.Middlewares.RandomRequestUaMiddleware': 400,
    },
}

# 打开 mysql 引擎开关，用于数据入库前更新逻辑判断
mysql_engine_off = True
```

###  2.2. yield item

在 `yield item` 时，要把需要存储的数据放到 `alldata` 字段中，程序会自动创建 `Table_Enum` 中的所依赖的数据表：`Mysql` 和 `MongoDB` 等各种存储的场景下都推荐此写法，写法风格如下：

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

`mysql_engine` 用于 `Mysql` 数据入库前的查询使用：

```python
sql = '''select `id` from `{}` where `article_detail_url` = "{}" limit 1'''.format(self.custom_settings['MYSQL_TABLE_PREFIX'] + Table_Enum.aritle_list_table.value['value'], article_detail_url)
df = pandas.read_sql(sql, self.mysql_engine)
```

`MongoDB` 场景下自带去重，只需指定去重条件 `mongo_update_rule` 即可：

```python
# mongo_update_rule 的字段为去重判断条件，这里是指 article_detail_url 字段为 article_detail_url 参数的数据存在则更新，不存在则新增
AritleInfoItem['mongo_update_rule'] = {"article_detail_url": article_detail_url}
```

### 2.4. 中间件及 pipelines 介绍

> 详细说明暂略，请看此项目 `spiders` 中的文件

若要使用具体场景下的 `middlewares` 或 `pipelines` 时，激活它即可。

## 3. 图片示例

如果不存在目标数据库，数据表或表字段，则自动创建项目所依赖的数据库，数据表和表字段及字段说明。

下图为 `demo_one` 的 `Mysql` 取本地配置 `LOCAL_MYSQL_CONFIG` 下的运行示例：

![image-20220803151448062](DemoSpider/doc/image-20220803151448062.png)

下图为 `demo_two` 的 `MongDB` 存储的场景下的示例：

![image-20220807170330444](DemoSpider/doc/image-20220807170330444.png)

下图为 `demo_three` 的 `Mysql` 取 `consul` 应用管理中心的配置下的运行示例：

**要运行此示例时，如果 `LOCAL_MYSQL_CONFIG` 在 `settings` 全局中有设置的话，请把它给去除。因为项目会优先从本地的配置中取配置，如果本地不存在 `LOCAL_MYSQL_CONFIG` 配置时，且 `APP_CONF_MANAGE` 为 `True` 时，当前的 `spiders` 才会从 `consul` 的应用管理中心中取相应配置。**

![image-20220807170520647](DemoSpider/doc/image-20220807170520647.png)

下图为 `demo_four` 的 `MongoDB` 取 `consul` 应用管理中心的配置下的运行示例：

![image-20220807223716593](DemoSpider/doc/image-20220807223716593.png)
