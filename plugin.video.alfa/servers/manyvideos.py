# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector manyvideos By Alfa development Group
# --------------------------------------------------------
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int
from core import httptools
from core import scrapertools
from platformcode import logger
import base64
from lib import jsunpack

def test_video_exists(page_url):

    response = httptools.downloadpage(page_url)
    if not response.sucess or \
       "Not Found" in response.data \
       or "File was deleted" in response.data \
       or "is no longer available" in response.data:
        return False, "[manyvideos] El fichero no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info()
    video_urls = []
    data = httptools.downloadpage(page_url).data
    data = scrapertools.find_single_match(data, 'JuicyCodes.Run\(([^\)]+)\)')
    data = data.replace("\"+\"", "")
    data = base64.b64decode(data)
    if PY3 and isinstance(data, bytes):
        data = data.decode('utf-8')
    unpack = jsunpack.unpack(data)
    matches = scrapertools.find_multiple_matches(unpack, '"file":"([^"]+)","label":"([^"]+)"')
    for url,quality in matches:
        url = url.replace("v1.", "v2.")
        video_urls.append(["[manyvideos] %s" % quality, url])
    return video_urls

