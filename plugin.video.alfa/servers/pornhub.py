# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector pornhub By Alfa development Group
# --------------------------------------------------------

from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    response = httptools.downloadpage(page_url)
    if not response.sucess or \
       "Not Found" in response.data \
       or "File was deleted" in response.data \
       or "removed" in response.data \
       or not "defaultQuality" in response.data \
       or "is no longer available" in response.data:
        return False, "[pornhub] El fichero no existe o ha sido borrado"
    return True, ""

def get_video_url(page_url, user="", password="", video_password=""):
    logger.info()
    video_urls = []
    data = httptools.downloadpage(page_url).data
    data = scrapertools.find_single_match(data, '<div id="vpContentContainer">(.*?)</script>')
    data = data.replace('" + "', '')
    videourl = scrapertools.find_multiple_matches(data, 'var quality_(\d+)p=(.*?);')
    scrapertools.printMatches(videourl)
    for scrapedquality,scrapedurl in videourl:
        orden = scrapertools.find_multiple_matches(scrapedurl, '\*\/([A-z0-9]+)')
        logger.debug(orden)
        url= ""
        for i in orden:
            url += scrapertools.find_single_match(data, '%s="([^"]+)"' %i)
        logger.debug(url)
        video_urls.append([scrapedquality + "p [pornhub]", url])
    return video_urls
