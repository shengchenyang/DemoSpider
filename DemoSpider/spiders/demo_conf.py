"""
场景介绍：
一些 scrapy 第三方扩展需要在 settings.py 中设置一些配置，涉及到 host，密码等隐私配置，直接展
示在 settings.py 里是不可接受的，这里预发布包提供一种功能来解决。

测试介绍：
测试在 settings.py 中赋值重要参数时，可以从 .conf 中获取自定义配置内容，来达到隐藏隐私内容和
保持配置内容统一存放的目的；

1. 介绍本项目中 settings.py 对应的赋值代码为：
redis_host = _my_cfg["my_add_redis"].get("host", "localhost")
redis_port = _my_cfg["my_add_redis"].getint("port", 6379)
redis_password = _my_cfg["my_add_redis"].get("password", None)

2. 项目中 .conf 对应的赋值代码为：
[my_add_redis]
host=localhost
port=6379
password=please_write_your_password_here

你也可以参考 .conf_example 中的示例。

请注意：
    - 正常情况下，在 settings.py 中导入是不需要 try catch 的，也不用添加任何条件判断语句，这
    是为了测试预发布版本的功能时，不影响旧项目运行；
    - 若您安装了预发布包，可尝试清除这些内容，是很优雅简洁的，等后续正式发布时，我会清理这部分；
    - 功能虽已在预发布阶段，但请不要在正式环境中使用预发布包；安装预发布版本命令如下：
    pip install git+https://github.com/shengchenyang/AyugeSpiderTools.git
"""

from typing import Any

from ayugespidertools.spiders import AyuSpider

from DemoSpider.common.types import ScrapyResponse

try:
    from DemoSpider.settings import redis_host, redis_password, redis_port
except ImportError:
    # 这里是为了测试预发布版本，且不影响旧项目运行，正常也是不需要 try catch 的。
    redis_host = redis_port = redis_password = None


class DemoConfSpider(AyuSpider):
    name = "demo_conf"
    allowed_domains = ["ayugespidertools.readthedocs.io"]
    start_urls = ["https://ayugespidertools.readthedocs.io"]
    custom_settings = {
        "REDIS_HOST": redis_host,
        "REDIS_PORT": redis_port,
        "REDIS_PARAMS": {"password": redis_password, "db": 8},
    }

    def parse(self, response: ScrapyResponse, **kwargs: Any) -> Any:
        if any([redis_host is None, redis_port is None, redis_password is None]):
            self.slog.error(
                "您应该是没有安装预发布包，或没有在 .conf 中配置 my_add_redis 部分，请参考 .conf_example 的 my_add_redis 部分。"
            )

        # 正常情况就可以获取到 .conf 中的重要的隐私配置了
        assert all(
            [
                redis_host == self.custom_settings["REDIS_HOST"],
                redis_port == self.custom_settings["REDIS_PORT"],
                redis_password == self.custom_settings["REDIS_PARAMS"]["password"],
            ]
        )
        self.slog.debug(
            f"测试成功，获取到 settings.py 中的隐私配置: {self.custom_settings}"
        )
