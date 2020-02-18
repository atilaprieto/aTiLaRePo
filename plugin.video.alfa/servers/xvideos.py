# -*- coding: utf-8 -*-
import re
from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global data
    
    data = httptools.downloadpage(page_url).data
    if "Lo sentimos" in data or "File not found" in data or 'og:video">' in data:
        return False, "[Xvideos] El archivo no existe o ha sido borrado"

    return True, ""


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).data
    patron = 'html5player.setVideo(?:Url|H)(\w+)\(\'([^\']+)\'\)'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for quality,url in matches:
        if "LS" in quality: quality = "HLS"
        video_urls.append(["[xvideos] %s" %quality, url])
    return video_urls
