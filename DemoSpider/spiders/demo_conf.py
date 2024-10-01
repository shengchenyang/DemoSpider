"""
场景介绍：
一些 scrapy 第三方扩展需要在 settings.py 中设置一些配置，涉及到 host，密码等隐私配置，直接展
示在 settings.py 里是不可接受的，这里预发布包提供一种功能来解决。

测试介绍：
测试在 settings.py 中赋值重要参数时，可以从 VIT_DIR 的 .conf 中获取自定义配置内容，来达到隐
藏隐私内容和保持配置内容统一存放的目的；

1. 介绍本项目中 settings.py 对应的赋值代码为：
redis_host = _my_cfg["my_add_redis"].get("host", "localhost")
redis_port = _my_cfg["my_add_redis"].getint("port", 6379)
redis_password = _my_cfg["my_add_redis"].get("password", None)

2. 项目中 .conf 对应的赋值代码示例为：
[my_add_redis]
host=localhost
port=6379
password=please_write_your_password_here

你也可以参考 .conf_example 中的示例。

请注意：
    - 可以在 settings.py 中使用 get_cfg 方法来获取自定义的隐私配置，也可以在对应的 spider
     (比如此处)中的 custom_settings 中直接使用，不再举例。
"""

from typing import Any

from ayugespidertools.spiders import AyuSpider

from DemoSpider.common.types import ScrapyResponse
from DemoSpider.settings import (  # 直接从 settings.py 中导入 .conf 中的自定义配置
    redis_host,
    redis_password,
    redis_port,
)


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
                "您安装的 ayugespidertools 版本没有在 3.10.0 及以上，或没有在 .conf 中配置示例所"
                "需的 my_add_redis 部分，请参考 .conf_example 的 my_add_redis 部分。"
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
