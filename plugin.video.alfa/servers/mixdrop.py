# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector Mixdrop By Alfa development Group
# --------------------------------------------------------

import re
from core import httptools
from core import scrapertools
from lib import jsunpack
from platformcode import logger

def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global data
    data = httptools.downloadpage(page_url).data
    if "<h2>WE ARE SORRY</h2>" in data or '<title>404 Not Found</title>' in data:
        return False, "[Mixdrop] El fichero no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []
    ext = '.mp4'
    
    packed = scrapertools.find_single_match(data, r'(eval.*?)</script>')
    unpacked = jsunpack.unpack(packed)
    
    media_url = scrapertools.find_single_match(unpacked, r'MDCore.vsrc\s*=\s*"([^"]+)"')
    if not media_url.startswith('http'):
        media_url = 'http:%s' % media_url
    video_urls.append(["%s [Mixdrop]" % ext, media_url])

    return video_urls
