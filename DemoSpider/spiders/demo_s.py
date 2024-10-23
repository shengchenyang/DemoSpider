"""
最简单的分布式，并发程序的示例：
此部分是简单实现分布式及并发 spider 程序的示例，使得优雅和方便地实现分布式，并发及部署运行

Note:
    1. 跑通这个示例需要安装 aio-pika，可通过此项目根目录中 pip install -r requirements.txt 安装；
    2. 可通过项目根目录下的 AsyncDockerfile 来打包和运行，打包命令为：
        docker build -t demo_s -f AsyncDockerfile .

        运行命令为：
        docker run -d --name="demos" -e task_num=2 demo_s
        这个命令是指在命令运行的设备上开启 task_num 个 demo_s 的程序，然后也可以在其它各种地方也部署
        此命令，来完成分布式部署。当然也可以不用 docker 的方式，使用 scrapy 管理平台等都行，看你自己
        的工作流水线设计。
"""

import json
from typing import Any

from ayugespidertools.spiders import AyuSpider
from scrapy.http import Request

from DemoSpider.common.types import ScrapyResponse

try:
    import aio_pika
except ImportError:
    # pip install aio-pika
    from DemoSpider.common.types import aio_pika


class DemoSSpider(AyuSpider):
    name = "demo_s"
    allowed_domains = ["ayugespidertools.readthedocs.io"]
    start_urls = ["data:,"]

    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            # 随机请求头
            "ayugespidertools.middlewares.RandomRequestUaMiddleware": 400,
        },
        # "LOGURU_ENABLED": False,
        "CONCURRENT_REQUESTS": 100,
        "DOWNLOAD_DELAY": 0.01,
    }

    async def parse(self, response: ScrapyResponse, **kwargs: Any) -> Any:
        connection = await aio_pika.connect_robust(
            host=self.rabbitmq_conf.host,
            port=self.rabbitmq_conf.port,
            user=self.rabbitmq_conf.username,
            password=self.rabbitmq_conf.password,
            virtualhost=self.rabbitmq_conf.virtualhost,
        )

        async with connection:
            queue_name = self.rabbitmq_conf.queue
            # Creating channel
            channel: aio_pika.abc.AbstractChannel = await connection.channel()
            # Declaring queue
            queue: aio_pika.abc.AbstractQueue = await channel.declare_queue(
                queue_name,
                durable=True,
                auto_delete=False,
            )

            async with queue.iterator() as queue_iter:
                # Cancel consuming after __aexit__
                async for message in queue_iter:
                    async with message.process():
                        body = message.body
                        task_info = json.loads(body.decode())

                        # 这里就可以写消费 mq 的任务消息，来分发采集新增/更新任务，配合 mongodb 场景
                        # 的 _mongo_update_rule 或 mysql 场景的
                        yield Request(
                            url="https://ayugespidertools.readthedocs.io/en/latest/",
                            callback=self.parse_next,
                            cb_kwargs={"task_info": task_info},
                            dont_filter=True,
                        )

    def parse_next(self, response: ScrapyResponse, task_info: dict) -> Any:
        self.slog.warning(f"{response.url} --- {task_info}")
