# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector mangoplay By Alfa development Group
# --------------------------------------------------------

from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url).data
    if "no longer exists" in data or "to copyright issues" in data:
        return False, "[mangoplay] El video ha sido borrado"
    return True, ""


def get_video_url(page_url, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).data
    url = scrapertools.find_single_match(data, 'shareId = "([^"]+)')
    url = httptools.downloadpage(url, follow_redirects=False, only_headers=True).headers.get("location", "")
    url = url.replace(" ","%20")
    video_urls.append([".MP4 [mangoplay]", url])

    return video_urls
