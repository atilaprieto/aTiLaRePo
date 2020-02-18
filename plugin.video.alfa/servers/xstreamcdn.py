# -*- coding: utf-8 -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    #from future import standard_library
    #standard_library.install_aliases()
    import urllib.parse as urllib                               # Es muy lento en PY2.  En PY3 es nativo
else:
    import urllib                                               # Usamos el nativo de PY2 que es más rápido

from core import httptools
from core import scrapertools
from core import jsontools
from platformcode import logger, config


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url).data
    if "ile was deleted" in data or "Page Cannot Be Found" in data or "<title>Sorry 404 not found" in data:
        return False, "[xstreamcdn.com] El archivo ha sido eliminado o no existe"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []
    post = {}
    post = urllib.urlencode(post)
    data = httptools.downloadpage("https://xstreamcdn.com/api/source/" + scrapertools.find_single_match(page_url, "/v/([A-z0-9_-]+)"), post=post, add_referer=page_url).data
    
    json_data = jsontools.load(data)
    check = json_data['success']
    if check == True:
        for element in json_data['data']:
            media_url = element['file']
            res = element['label']
            tipo = element['type']
            video_urls.append([tipo + " (" + res + ") [xstreamcdn]", media_url])
    return video_urls
