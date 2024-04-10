from typing import Union

from scrapy.http import Response
from scrapy.http.response.html import HtmlResponse
from scrapy.http.response.text import TextResponse
from scrapy.http.response.xml import XmlResponse

ScrapyResponse = Union[TextResponse, XmlResponse, HtmlResponse, Response]


class RedisSpider: ...
