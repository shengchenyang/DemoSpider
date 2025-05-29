# DemoSpider 项目说明文档

## 前言
本项目用于提供 `AyugeSpiderTools` 具体场景示例，由于此项目会经常变动，所以独立成为一个专属项目，而不是放入 `AyugeSpiderTools` 项目的示例中。

详细的文档说明，还是根据 [ayugespidertools readthedocs](https://ayugespidertools.readthedocs.io/en/latest/) 说明为主。

## 1. 前提条件

> `python 3.8+` 可以直接输入以下命令：

```shell
pip install ayugespidertools

# 某些场景可能需要安装全部依赖，可查看对应的 spider 脚本头注释，会有相关提示：
pip install ayugespidertools[all]
```

### 1.1. 运行方法

先根据复现场景配置本项目中 `VIT` 下的 `.conf` 对应信息，后续运行方式和普通 `scrapy` 项目一致，比如：
1. 直接运行你所关心的 `spider` 即可，是选择通过 `run.py`，`run.sh` 还是直接 `scrapy` 命令都可以；
2. 使用各种爬虫管理平台运行也可以，比如 `scrapydweb`，`crawlab` 等；
3. 也可以使用 `docker` 运行的方式，项目中也给出了 `Dockerfile` 示例。

> 这里补充下 `docker` 运行部分：

```shell
# 构建镜像，在 Dockerfile 所在的项目目录中执行：
docker build -t demo_spider -f Dockerfile .

# 执行命令示例，这里以 demo_five 的 spider 为例：
docker run --name demo_five -e spider_name=demo_five demo_spider
```

> NOTE：

- 若不清楚 `.conf` 如何配置，项目中已给出 `.conf_example` 的示例文件，请对照你想复现的场景按需配置。
- 如果对各项配置不太了解，请在对应的 [readthedocs](https://ayugespidertools.readthedocs.io/en/latest/topics/configuration.html) 文档中查看介绍。
- 项目中各 `spiders` 脚本功能及场景介绍请在 `AyugeSpiderTools` 的 `readme` 中查看，这里不再重复。
- 本项目有不同分支，请根据不同版本分支来测试对应版本的 `ayugespidertools` 库，`main` 则表示为最新版本分支。
- 此项目中的各个场景的 `spiders` 过多，如果感觉场景复现繁琐，建议创建一个新项目来实现你感兴趣的 `spider`。

### 1.2. 关于项目结构

如果想快速生成类似此项目的结构，推荐使用 [LazyScraper](https://github.com/shengchenyang/LazyScraper) 来快速创建工程项目。

## 2. 运行结果图示

如果不存在目标数据库，数据表或表字段，则自动创建项目所依赖的数据库，数据表和表字段及字段说明。

注：以下运行截图非覆盖全场景，请自行查看本项目中 `spdier` 的各脚本内容。

> 下图为 `demo_one` 的 `Mysql` 取本地配置下的运行示例：
>

![image-20220803151448062](DemoSpider/docs/images/image-20220803151448062.png)

> 下图为 `demo_two` 的 `MongDB` 存储的场景下的示例：
>

![image-20220807170330444](DemoSpider/docs/images/image-20220807170330444.png)

> 下图为 `demo_three` 的 `Mysql` 取 `consul` 中的配置下的运行示例：
>

**要运行此示例时，只需配置 `APP_CONF_MANAGE` 为 `True`，且在 `.conf` 中设置 `CONSUL` 相关配置后，当前的 `spiders` 即从 `consul` 中取相应配置。**

![image-20220807170520647](DemoSpider/docs/images/image-20220807170520647.png)

> 下图为 `demo_four` 的 `MongoDB` 取 `consul` 中的配置下的运行示例：
>

![image-20220807223716593](DemoSpider/docs/images/image-20220807223716593.png)

> 下图为 `demo_proxy_one` 的快代理动态隧道代理运行示例：

![image-20220905112615892](DemoSpider/docs/images/image-20220905112615892.png)
