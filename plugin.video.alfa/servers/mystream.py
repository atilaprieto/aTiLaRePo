# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector mystream By Alfa development Group
# --------------------------------------------------------
from core import httptools
from core import scrapertools
from lib import js2py
from platformcode import logger, config


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url)
    global page_data
    page_data = data.data
    if data.code == 404:
        return False, config.get_localized_string(70449) % "mystream"
    if "<title>video is no longer available" in data.data or "<title>Video not found" in data.data or "We are unable to find the video" in data.data:
        return False, config.get_localized_string(70449) % "mystream"
    return True, ""

def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    global page_data
    dec = scrapertools.find_single_match(page_data, '(\$=~\[\];.*?\(\)\))\(\);')
    # needed to increase recursion
    import sys
    sys.setrecursionlimit(10000)

    deObfCode = js2py.eval_js(dec)

    video_urls.append(['mp4 [mystream]', scrapertools.find_single_match(str(deObfCode), "'src',\s*'([^']+)")])
    return video_urls