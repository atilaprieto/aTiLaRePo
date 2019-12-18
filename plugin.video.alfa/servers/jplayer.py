# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector jplayer By Alfa development Group
# --------------------------------------------------------

import urllib

from core import httptools
from core import jsontools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url).data
    if "no longer exists" in data or "to copyright issues" in data:
        return False, "[jplayer] El video ha sido borrado"
    return True, ""


def get_video_url(page_url, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    post = urllib.urlencode({"r":"", "d":"www.jplayer.net"})
    data = httptools.downloadpage(page_url, post=post).data
    json = jsontools.load(data)["data"]
    for _url in json:
        url = _url["file"]
        label = _url["label"]
        video_urls.append([label +" [jplayer]", url])

    return video_urls
