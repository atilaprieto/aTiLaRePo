# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector verystream By Alfa development Group
# --------------------------------------------------------

import re
from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url)
    if data.code == 404 or '<h3>File not found' in data.data:
        return False, "[verystream] El archivo no existe o ha sido borrado"
    if "<title>video is no longer available" in data.data:
        return False, "[verystream] El archivo no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, premium = False, user = "", password = "", video_password = ""):
    logger.info("url=" + page_url)
    video_urls = []
    headers = {'referer': page_url}
    data = httptools.downloadpage(page_url, headers=headers).data
    sub = scrapertools.find_single_match(data, '<track src="([^"]+)"')
    videolink = scrapertools.find_single_match(data, 'id="videolink">([^<]+)<')
    url = "https://verystream.com/gettoken/%s?mime=true" %videolink
    url = httptools.downloadpage(url, follow_redirects=False, only_headers=True).headers.get("location", "")
    video_urls.append(['verystream [mp4]' ,url, 0, sub])
    return video_urls
