# DemoSpider 项目说明文档

## 前言
本文是对 `AyugeSpiderTools` 工具的使用进行具体场景实现，由于此项目会经常变动和修改，所以独立成为一个专属项目，而不是放入 `AyugeSpiderTools` 项目的示例中。

详细的文档说明，还是根据 [ayugespidertools readthedocs](https://ayugespidertools.readthedocs.io/en/latest/) 说明为主。

## 1. 前提条件

> `python 3.8+` 可以直接输入以下命令：

```shell
pip install ayugespidertools

# 某些场景可能需要安装全部依赖，可查看对应的 spider 脚本头注释，会有相关提示：
pip install ayugespidertools[all]
```

### 1.1. 运行方法

1. 只需要补充本项目中 `VIT` 下的 `.conf` 配置内容即可。
2. 然后，运行你所关心的 `spider` 即可。（是选择通过 `run.py`，`run.sh` 还是直接 `scrapy` 命令都可以。）

> 补充：

- 若不清楚 `.conf` 如何配置，项目中已给出 `.conf_example` 的示例文件，请对照你想复现的场景按需配置。
- 如果对各项配置不太了解，请在对应的 [readthedocs](https://ayugespidertools.readthedocs.io/en/latest/topics/configuration.html) 文档中查看介绍。
- 项目中各 `spiders` 脚本功能及场景介绍请在 `AyugeSpiderTools` 的 `readme` 中查看，这里不再重复。
- 本项目有不同分支，请根据不同版本分支来测试对应版本的 `ayugespidertools` 库，`main` 则表示为最新版本分支。

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
