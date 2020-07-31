# -*- coding: utf-8 -*-
from core import httptools
from core import scrapertools
from platformcode import logger



def test_video_exists(page_url):
    global data
    logger.info("(page_url='%s')" % page_url)
    response = httptools.downloadpage(page_url)

    if response.code == 404 or "This page is not available" in response.data:
        return False, "[Youporn] El archivo no existe o ha sido borrado"
    else:
        data = response.data
    return True, ""


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    patron  = '"format":"","quality":"([^"]+)","videoUrl":"([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for quality, scrapedurl in matches:
        url =  scrapedurl.replace("\/", "/").replace("\u0026", "&")
        video_urls.append(["[youporn] %sp" %quality, url])
    return video_urls

