# -*- coding: utf-8 -*-

from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    data = scrapertools.httptools.downloadpage(page_url).data
    url = scrapertools.find_single_match(data, '<source src="([^"]+)"')
    video_urls.append(["[Sharedvid]", url])
    return video_urls
