import json
from DemoSpider.settings import logger


__all__ = [
    "Operations",
]


class Operations(object):
    """
    项目依赖方法
    """

    @staticmethod
    def parse_response_data(response_data: str, mark: str):
        """
        解析测试请求中的内容，并打印基本信息
        Args:
            response_data: 请求响应内容
            mark: 请求标识

        Returns:
            args: request args
            headers: request headers
            origin: request origin
            url: request url
        """
        logger.info(f"mark: {mark}, content: {response_data}")
        json_data = json.loads(response_data)
        args = json_data["args"]
        headers = json_data["headers"]
        origin = json_data["origin"]
        url = json_data["url"]
        logger.info(f"{mark} response, args: {args}")
        logger.info(f"{mark} response, headers: {headers}")
        logger.info(f"{mark} response, origin: {origin}")
        logger.info(f"{mark} response, url: {url}")
        return args, headers, origin, url
