# -*- coding: utf-8 -*-
import re
from core import httptools
from core import scrapertools
from platformcode import logger


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).data
    url = scrapertools.find_single_match(data, '{"url":"([^"]+)"')
    url =  url.replace("\/", "/")
    url = "https://xhamster.com%s" % url
    data = httptools.downloadpage(url).data
    patron = ',NAME="([0-9]+p)".*?(https:.*?.mp4)'
    matches = scrapertools.find_multiple_matches(data, patron)
    for quality,scrapedurl  in matches:
        video_urls.append(["[xhamster] %s" %quality, url])
    return video_urls

