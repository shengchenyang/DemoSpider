from __future__ import annotations

from scrapy.http import Response
from scrapy.http.response.html import HtmlResponse
from scrapy.http.response.json import JsonResponse
from scrapy.http.response.text import TextResponse
from scrapy.http.response.xml import XmlResponse

ScrapyResponse = TextResponse | XmlResponse | HtmlResponse | Response | JsonResponse


class RedisSpider: ...


class AIO_PIKA: ...


aio_pika = AIO_PIKA()
