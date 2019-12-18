# -*- coding: utf-8 -*-

from core import httptools
from core import scrapertools
from platformcode import logger

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url).data
    if "Archive no Encontrado" in data or  "File has been removed" in data:
        return False, "[bitertv] El fichero ha sido borrado"
    return True, ""


def get_video_url(page_url, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).data
    patron = "(?s)file: '([^']+)"
    file = scrapertools.find_single_match(data, patron)
    video_urls.append([".MP4 [bitertv]", file])
    return video_urls
