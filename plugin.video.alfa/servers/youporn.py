# -*- coding: utf-8 -*-
from core import httptools
from core import scrapertools
from platformcode import logger


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).data
    patron  = '"format":"","quality":"([^"]+)","videoUrl":"([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for quality, scrapedurl in matches:
        url =  scrapedurl.replace("\/", "/").replace("\u0026", "&")
        video_urls.append(["[youporn] %sp" %quality, url])
    return video_urls
