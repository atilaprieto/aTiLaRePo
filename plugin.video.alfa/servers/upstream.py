# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector Upstream By Alfa development Group
# --------------------------------------------------------

import re
from core import httptools
from core import scrapertools
from platformcode import logger
from lib import jsunpack

page = ''

def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global page
    page = httptools.downloadpage(page_url)

    if page.code == 404 or 'File is no longer available' in page.data:
        return False, "[upstream] El archivo no existe o  ha sido borrado"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    data = page.data
    video_urls = []
    packed = scrapertools.find_single_match(data, "text/javascript'>(eval.*?)\s*</script>")
    if packed:
        data = jsunpack.unpack(packed)
        logger.error(data)
    patron = 'file:"([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for url in matches:
        ext = url[-4:]
        if ext == '.srt':
            continue
        url += '|Referer=%s' % page_url
        video_urls.append(["%s [Upstream]" % ext, url])

    return video_urls
