import re

import requests
from urllib3.exceptions import MaxRetryError


class UrlChecker:
    """
    This class is used to check if a URL is valid in all of its forms (format and reachable via browser).
    """

    @staticmethod
    def check_format(url) -> bool:
        """
        This method checks if a url is well-formatted (validator like).
        :param url: Url to validate.
        :return: True if the URL is valid, otherwise False.
        """

        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https:// or ftp:// or ftps://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        return regex.match(str(url))

    @staticmethod
    def check_exists(url) -> bool:
        """
        This method checks if a website URL is reachable using requests library. It send a HTTP GET
        requests and reads the response code.

        :param url: Url of the website to check if it is reachable.
        :return: True if the HTTP response code is equals to 200, otherwise False.
        """

        try:
            request = requests.get(str(url))
            return request.status_code == 200

        except (MaxRetryError, requests.exceptions.ConnectionError):
            return False

    @staticmethod
    def full_check(url):
        """
        This method uses 'check_format' and 'check_exists' to fully check a url.
        :param url: Url to check.
        :return: True if the url passes all the checks, otherwise False.
        """
        return UrlChecker.check_format(url) and UrlChecker.check_exists(url)
