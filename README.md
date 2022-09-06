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

### 1.1. 运行方法

> 本扩展库用于方便 `python` 开发，本项目的应用场景的运行方法为：

只需要将本项目中的 `VIT` 文件夹下的 `.conf` 文件如下编辑，然后 `scrapy crawl xxxx` 对应的 `spiders` 脚本即可。

> `VIT` 文件夹中的 `.conf` 文件内容为，已脱敏，请按需自行配置：

```ini
[MYSQL]
HOST=***
PORT=3306
USER=***
PASSWORD=***
DATABASE=***
CHARSET=***

[PYMYSQL_CONNECT]
CONFIG_DICT={'host': '***', 'port': 3306, 'user': '***', 'password': '***', 'database': '***', 'charset': 'utf8mb4'}

[MONGODB]
HOST=***
PORT=27017
DATABASE=***
AUTHSOURCE=***
USER=***
PASSWORD=***

[WWXRobot]
key=***

[MONGODB_URI]
CONN_URI=***

[ALI_OSS]
OSSACCESSKEYID=***
OSSACCESSKEYSECRET=***
ENDPOINT=***
EXAMPLEBUCKET=***
OPERATEDOC=***
```

> 项目中各 `spiders` 脚本名称及其对应功能介绍，如下：

```diff
# 采集数据存入 `Mysql` 的场景：
- 1).demo_one: 配置根据本地 `settings` 的 `LOCAL_MYSQL_CONFIG` 中取值
+ 3).demo_three: 配置根据 `consul` 的应用管理中心中取值
+ 5).demo_five: 异步存入 `Mysql` 的场景

# 采集数据存入 `MongoDB` 的场景：
- 2).demo_two: 采集数据存入 `MongoDB` 的场景（配置根据本地 `settings` 的 `LOCAL_MONGODB_CONFIG` 中取值）
+ 4).demo_four: 采集数据存入 `MongoDB` 的场景（配置根据 `consul` 的应用管理中心中取值）
+ 6).demo_six: 异步存入 `MongoDB` 的场景

# 将 `Scrapy` 的 `Request`，`FormRequest` 替换为其它工具实现的场景
- 以上为使用 scrapy Request 的场景
+ 7).demo_seven: scrapy Request 替换为 requests 请求的场景(一般情况下不推荐使用，同步库会拖慢 scrapy 速度，可用于测试场景)

+ 8).demo_eight: 同时存入 Mysql 和 MongoDB 的场景

- 9).demo_aiohttp_example: scrapy Request 替换为 aiohttp 请求的场景，提供了各种请求场景示例（GET,POST）
+ 10).demo_aiohttp_test: scrapy aiohttp 在具体项目中的使用方法示例

+ 11.demo_proxy_one: 快代理动态隧道代理示例
+ 12).demo_proxy_two: 测试快代理独享代理
```


## 2. 使用 ayugespidertools

> 以下只对项目的总体配置和一些注意点进行简要说明，因为只要你懂得 `Scrapy` 框架，那么项目中的配置对你来说也极易上手。而且项目中的代码注释也较详细，并不难理解。

使用以下命令来创建项目模板：

```shell
ayugespidertools startproject <projectName>
```

使用以下命令来创建 `spider` 脚本模板：

```shell
# 先进入对应的项目中
cd <projectName>
ayugespidertools genspider <spiderName> <domain>
```

注：其实是和 `scrapy` 命令一致的，也是兼容的，比如直接使用 `scrapy` 命令，然后手动设置相关配置也是可以的。

###  2.1. 项目的配置说明

> 本项目中的所涉及到的配置，可以放在 `settings` 和 `custom_setting` 任意地方中（只是**优先级 settings < ayuspider inner_settings < custom_settings**；如果**多处重复设置，则会根据优先级覆盖内容**），根据应用场景来决定。比如，如果你开发的项目所有脚本需要存储到同一个数据库中，那么将数据库相关配置统一放在 `settings` 中，或根据 consul 来远程获取配置信息会比较方便管理；若同个项目中不同脚本需要连接不同数据库等信息，则相关配置需要放在对应脚本的 `custom_setting` 中。

本项目中的 `settings` 配置信息是根据 [1.1. 运行方法](# 1.1. 运行方法) 中的 `.conf` 内容来关联信息的，不需要的配置就不管它即可。

> 在 `custom_setting` 中添加个性化的配置：

可以在 `spider` 中的各个脚本中添加其个性化的配置，比如随机请求头，优质账号对应的代理中间件等，具体请在本项目中的各个脚本中查看，不再赘述。

### 2.2. Item Loaders

`ayugespidertools` 扩展库使用了 `scrapy` 官方文档[推荐的 dataclass 方式](https://docs.scrapy.org/en/latest/topics/loaders.html?highlight=dataclass#working-with-dataclass-items)来替代 `scrapy Item` 对象（当然[也可以使用官方推荐的 attr.s 来替换](https://docs.scrapy.org/en/latest/topics/items.html?highlight=attr.s#attr-s-objects)），可以很方便地、优雅的序列化和约束需要存储的字段类型，设置默认值等等功能。

> 在 `yield item` 时，要把需要存储的数据放到 `alldata` 字段中，程序会自动创建 `Table_Enum` 中的所依赖的数据库，数据表，表字段及字段注释：`Mysql` 和 `MongoDB` 等各种存储的场景下都推荐此写法，写法风格如下：
>

```python
# 非常推荐此写法，article_info 含有所有需要存储至表中的字段
article_info = {
    "article_detail_url": {'key_value': article_detail_url, 'notes': '文章详情链接'},
    "article_title": {'key_value': article_title, 'notes': '文章标题'},
    "comment_count": {'key_value': comment_count, 'notes': '文章评论数量'},
    "favor_count": {'key_value': favor_count, 'notes': '文章赞成数量'},
    "nick_name": {'key_value': nick_name, 'notes': '文章作者昵称'}
}

ArticleInfoItem = MysqlDataItem(
    alldata=article_info,
    table=Table_Enum.article_list_table.value['value'],
)
logger.info(f"ArticleInfoItem: {ArticleInfoItem}")
yield ArticleInfoItem
```

### 2.3. 去重查询

#### 2.3.1. Mysql 场景

> 当需要在` mysql` 场景下的存储数据前进行更新策略时，需要在对应的 ` spider` 脚本中打开 `mysql` 引擎开关，即：

```python
mysql_engine_enabled = True
```

`mysql_engine` 用于 `Mysql` 数据入库前的查询使用：

```python
sql = '''select `id` from `{}` where `article_detail_url` = "{}" limit 1'''.format(self.custom_settings['MYSQL_TABLE_PREFIX'] + Table_Enum.article_list_table.value['value'], article_detail_url)
df = pandas.read_sql(sql, self.mysql_engine)
```

#### 2.3.2. MongoDB 场景

`MongoDB` 场景下自带去重，只需指定去重条件 `mongo_update_rule` 即可：

```python
# mongo_update_rule 的字段为去重判断条件，这里是指 article_detail_url 字段为 article_detail_url 参数的数据存在则更新，不存在则新增
ArticleInfoItem = MongoDataItem(
    # alldata 用于存储 mongo 的 Document 文档所需要的字段映射
    alldata=article_info,
    # table 为 mongo 的存储 Collection 集合的名称
    table=Table_Enum.article_list_table.value['value'],
    # mongo_update_rule 为查询数据是否存在的规则
    mongo_update_rule={"article_detail_url": article_detail_url},
)
```

### 2.4. 中间件及 pipelines 介绍

> 详细说明暂略，请看此项目 `spiders` 中的文件

若要使用具体场景下的 `middlewares` 或 `pipelines` 时，激活它即可。

## 3. 图片示例

如果不存在目标数据库，数据表或表字段，则自动创建项目所依赖的数据库，数据表和表字段及字段说明。

注：以下运行截图非覆盖全场景，请自行查看本项目中 `spdier` 的各脚本内容。

> 下图为 `demo_one` 的 `Mysql` 取本地配置 `LOCAL_MYSQL_CONFIG` 下的运行示例：
>

![image-20220803151448062](DemoSpider/doc/image-20220803151448062.png)

> 下图为 `demo_two` 的 `MongDB` 存储的场景下的示例：
>

![image-20220807170330444](DemoSpider/doc/image-20220807170330444.png)

> 下图为 `demo_three` 的 `Mysql` 取 `consul` 应用管理中心的配置下的运行示例：
>

**要运行此示例时，如果 `LOCAL_MYSQL_CONFIG` 在任意 `settings` 中有设置的话，请把它删除。因为项目会优先从本地的配置中取值，如果本地不存在 `LOCAL_MYSQL_CONFIG` 配置时，且 `APP_CONF_MANAGE` 为 `True` 时，当前的 `spiders` 才会从 `consul` 的应用管理中心中取相应配置。**

![image-20220807170520647](DemoSpider/doc/image-20220807170520647.png)

> 下图为 `demo_four` 的 `MongoDB` 取 `consul` 应用管理中心的配置下的运行示例：
>

![image-20220807223716593](DemoSpider/doc/image-20220807223716593.png)

> 下图为 `demo_proxy_one` 的快代理动态隧道代理运行示例：

![image-20220905112615892](DemoSpider/doc/image-20220905112615892.png)

