# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector pornrewind By Alfa development Group
# --------------------------------------------------------

from core import httptools
from core import scrapertools
from platformcode import logger

from lib.kt_player import decode

def test_video_exists(page_url):

    response = httptools.downloadpage(page_url)

    if not response.sucess or \
       "Not Found" in response.data \
       or "File was deleted" in response.data \
       or "is no longer available" in response.data:
        return False, "[pornrewind] El fichero no existe o ha sido borrado"

    global video_url, license_code
    video_url = scrapertools.find_single_match(response.data, "video_url: '([^']+)'")
    license_code = scrapertools.find_single_match(response.data, "license_code: '([^']+)'")

    return True, ""

def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info()
    # mediaurl = decode(video_url, license_code)
    mediaurl = video_url
    if not mediaurl.startswith("https"):
        mediaurl = "https://%s" % mediaurl
    return [["[pornrewind]", mediaurl]]