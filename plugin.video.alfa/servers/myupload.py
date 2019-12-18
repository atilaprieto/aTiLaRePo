# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector myupload By Alfa development Group
# --------------------------------------------------------
from core import httptools
from core import scrapertools
from platformcode import logger
import base64

def test_video_exists(page_url):

    response = httptools.downloadpage(page_url)

    if not response.sucess or \
       "Not Found" in response.data \
       or "File was deleted" in response.data \
       or "is no longer available" in response.data:
        return False, "[myupload] El fichero no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info()
    video_urls = []
    data = httptools.downloadpage(page_url).data
    matches = scrapertools.find_multiple_matches(data, 'tracker: "([^"]+)"')
    for scrapedurl in matches:
        url = base64.b64decode(scrapedurl)
    video_urls.append(["[myupload]", url])
    return video_urls