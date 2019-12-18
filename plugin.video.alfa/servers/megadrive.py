# -*- coding: utf-8 -*-

from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url).data
    if "no longer exists" in data or "to copyright issues" in data:
        return False, "[Megadrive] El video ha sido borrado"
    if "please+try+again+later." in data:
        return False, "[Megadrive] Error de Megadrive, no se puede generar el enlace al video"
    if "File has been removed due to inactivity" in data:
        return False, "[Megadrive] El archivo ha sido removido por inactividad"
    return True, ""


def get_video_url(page_url, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url).data
    video_urls = []
    videourl = scrapertools.find_single_match(data, "<source.*?src='([^']+)")
    video_urls.append([".MP4 [megadrive]", videourl])

    return video_urls
