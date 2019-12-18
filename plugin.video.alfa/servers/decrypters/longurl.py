# -*- coding: utf-8 -*-

import re
import urllib

from core import httptools
from core import scrapertools
from platformcode import logger


def get_server_list():
    servers = []
    data = httptools.downloadpage("http://longurl.org/services").data
    data = scrapertools.unescape(data)
    data = scrapertools.find_single_match(data, '<ol>(.*?)</ol>')
    patron = '<li>(.*?)</li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    # añadiendo algunos manualmente que no salen en la web
    servers.append("sh.st")

    for server in matches:
        servers.append(server)
    return servers


servers = get_server_list()


def get_long_urls(data):
    logger.info()
    patron = '<a href="http://([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for short_url in matches:
        if short_url.startswith(tuple(servers)):
            logger.info(": " + short_url)
            longurl_data = httptools.downloadpage(
                "http://api.longurl.org/v2/expand?url=" + urllib.quote_plus(short_url)).data
            logger.info(longurl_data)
            try:
                long_url = scrapertools.scrapertools.find_single_match(longurl_data, '<long-url><!\[CDATA\[(.*?)\]\]></long-url>')
            except:
                long_url = ""
            if (long_url <> ""): data = data.replace(short_url, long_url)
    return data
