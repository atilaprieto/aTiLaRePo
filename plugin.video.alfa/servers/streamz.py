# -*- coding: utf-8 -*-
import re
from core import httptools
from core import scrapertools
from platformcode import logger
from lib import jsunpack


def test_video_exists(page_url):
    global data
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url).data

    if "File not found, sorry!" in data:
        return False, "[streamz] El fichero no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    packed = scrapertools.find_single_match(data, r'(eval\(function\(p,a,c,k,e,d\).*?)\s+</script>')
    unpacked = jsunpack.unpack(packed)

    url = scrapertools.find_single_match(unpacked, '(https://streamz.*?/get.*?.dll)')
    url = url.replace("getmp4", "getlink")
    url = httptools.downloadpage(url, headers={"referer": page_url}, follow_redirects=False).headers["location"]
    video_urls.append(["[streamz]", url])
    return video_urls

