# -*- coding: utf-8 -*-
# -*- Server ZPlayer -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

from core import httptools
from core import scrapertools
from platformcode import logger
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

def test_video_exists(page_url):
    global data
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url, add_referer=True).data
    if "Page not found" in data:
        return False, "[ZPlayer] El fichero no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    patron = '"file": "([^"]+)",.*?"type": "([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for video_url, ext in matches:
        ref = scrapertools.find_single_match(video_url, '(.*?&)') + "shared=%s" % page_url
        headers = {"Referer":page_url}
        if "redirect"  in video_url: 
            url = httptools.downloadpage(video_url, headers=headers, follow_redirects=False, only_headers=True).headers.get("location", "")
            url += "|Referer=%s" %page_url
        else:
            url = video_url + "|Referer=%s" % ref
        video_urls.append(["[zplayer] %s" % ext, url])
    return video_urls
