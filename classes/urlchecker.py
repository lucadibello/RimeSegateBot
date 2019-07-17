import requests
from urllib3.exceptions import MaxRetryError
import re


class UrlChecker:

    @staticmethod
    def check_format(url) -> bool:
        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https:// or ftp:// or ftps://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        return regex.match(str(url))

    @staticmethod
    def check_exists(url) -> bool:
        try:
            request = requests.get(str(url))
            return request.status_code == 200

        except (MaxRetryError, requests.exceptions.ConnectionError):
            return False

    @staticmethod
    def full_check(url):
        return UrlChecker.check_format(url) and UrlChecker.check_exists(url)
