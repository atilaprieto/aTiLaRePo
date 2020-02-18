# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector Upstream By Alfa development Group
# --------------------------------------------------------

import re
from core import httptools
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    data = httptools.downloadpage(page_url)

    if data.code == 404:
        return False, "[upstream] El archivo no existe o  ha sido borrado"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)

    video_urls = []
    data = httptools.downloadpage(page_url).data
    patron = 'file:"([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for url in matches:
        video_urls.append(["[Upstream]", url])

    return video_urls
