# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector aparatcam By Alfa development Group
# --------------------------------------------------------

from core import httptools
from core import scrapertools
from platformcode import logger


# def test_video_exists(page_url):
    # data = httptools.downloadpage(page_url).data
    # if "File was deleted" in data or "eliminado" in data\
       # or "no está disponible" in data or "Page Not Found" in data:
        # return False, "[aparatcam] El video ha sido borrado o no existe"
    # return True, ""

def get_video_url(page_url, user="", password="", video_password=""):
    logger.info()
    video_urls = []
    data = httptools.downloadpage(page_url).data
    url = scrapertools.find_single_match(data, 'src: "([^"]+)"')
    video_urls.append(["aparatcam", url])
    return video_urls

