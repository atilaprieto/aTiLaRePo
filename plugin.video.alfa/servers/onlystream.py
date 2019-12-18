# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector Onlystream By Alfa development Group
# --------------------------------------------------------

import re, time
from core import httptools, scrapertools
from platformcode import logger, platformtools

data = ""
def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    data = httptools.downloadpage(page_url)

    if not data.sucess or "<h1>Oops! Sorry</h1>" in data.data or "File was deleted" in data.data or "is no longer available" in data.data:
        return False, "[Onlystream] El archivo no existe o  ha sido borrado"
    global data
    data = data.data
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)

    video_urls = []
    patron = '\{file:"([^"]+)"'
    #TODO comprobar fiabilidad de resolución indicada en la web
    matches = re.compile(patron, re.DOTALL).findall(data)

    for url in matches:
        ext = url[-4:]        
        video_urls.append(["%s [onlystream]" % (ext), url])

    return video_urls
