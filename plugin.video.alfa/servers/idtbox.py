# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector Idtbox By Alfa development Group
# --------------------------------------------------------

import re
from core import httptools, scrapertools
from platformcode import logger, platformtools

data = ""
def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global data
    data = httptools.downloadpage(page_url)

    if not data.sucess or "Not Found" in data.data or "File was deleted" in data.data or "is no longer available" in data.data:
        return False, "[Idtbox] El archivo no existe o  ha sido borrado"
    
    data = data.data
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    logger.error(data)
    video_urls = []
    patron = 'source src="([^"]+)" type="([^"]+)" res=(\d+)'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, ext, res in matches:
        res = res+'p'
        try:
            ext = ext.split("/")[1]
        except:
            ext = ".mp4"
        video_urls.append(["%s (%s) [idtbox]" % (ext, res), url])

    return video_urls
