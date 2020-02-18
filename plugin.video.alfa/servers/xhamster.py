# -*- coding: utf-8 -*-
import re
from core import httptools
from core import scrapertools
from platformcode import logger


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).data
    patron = '"fallback":"([^"]+)","quality":"([0-9]+p)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, quality  in matches:
        url =  scrapedurl.replace("\/", "/")
        video_urls.append(["[xhamster] %s" %quality, url])
    return video_urls
