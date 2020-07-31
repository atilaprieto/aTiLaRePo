# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector pornhub By Alfa development Group
# --------------------------------------------------------

from core import httptools
from core import scrapertools
from platformcode import logger


# def test_video_exists(page_url):
    # data = httptools.downloadpage(page_url).data
    # if "File was deleted" in data or "eliminado" in data\
       # or "no está disponible" in data or "Page Not Found" in data:
        # return False, "[pornhub] El video ha sido borrado o no existe"
    # return True, ""

def get_video_url(page_url, user="", password="", video_password=""):
    logger.info()
    video_urls = []
    data = httptools.downloadpage(page_url).data
    data = scrapertools.find_single_match(data, '<div id="vpContentContainer">(.*?)</script>')
    data = data.replace('" + "', '')
    videourl = scrapertools.find_multiple_matches(data, 'var quality_(\d+)p=(.*?);')
    for scrapedquality,scrapedurl in videourl:
        orden = scrapertools.find_multiple_matches(scrapedurl, '\*\/([A-z0-9]+)')
        url= ""
        for i in orden:
            url += scrapertools.find_single_match(data, '%s="([^"]+)"' %i)
        video_urls.append([scrapedquality + "p [pornhub]", url])
    return video_urls

