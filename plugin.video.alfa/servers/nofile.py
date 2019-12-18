# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector nofile By Alfa development Group
# --------------------------------------------------------

from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    response = httptools.downloadpage(page_url)
    if not response.sucess or "Not Found" in response.data or "File was deleted" in response.data or "is no longer available" in response.data:
        return False, "[nofile] El fichero no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).data
    url = scrapertools.find_single_match(data, '<source src="([^"]+)')
    url = httptools.downloadpage("https://nofile.io" + url, follow_redirects=False, only_headers=True).headers.get("location", "")
    title = "mp4 [nofile]"
    video_urls.append([title, url])
    return video_urls
