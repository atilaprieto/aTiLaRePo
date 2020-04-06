# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector Cinemaupload By Alfa development Group
# --------------------------------------------------------
import os
import re
import json
from core import httptools
from core import scrapertools
from platformcode import config
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global data

    if '|' in page_url:
        page_url, referer = page_url.split("|", 1)
    else:
        return video_urls

    headers = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X)',
               'Referer': referer
               }
    data = httptools.downloadpage(page_url, headers=headers).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    if data.code == 404:
        return False, "[CinemaUpload] El archivo no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)

    video_urls = list()
    referer = ''
    patron = 'file: "([^"]+)",'
    matches = scrapertools.find_multiple_matches(data, patron)

    for url in matches:
        url += "|Referer=%s" %page_url
        video_urls.append(['.m3u8 [CinemaUpload]', url])
    return video_urls
