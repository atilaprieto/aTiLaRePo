# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector DoodStream By Alfa development Group
# --------------------------------------------------------
import re
import base64
import time
from lib import js2py
from core import httptools
from core import scrapertools
from platformcode import logger

data = ""


def test_video_exists(page_url):
    global data
    logger.info("(page_url='%s')" % page_url)
    response = httptools.downloadpage(page_url)

    if response.code == 404:
        return False, "[Doodstream] El archivo no existe o ha sido borrado"
    else:
        data = response.data
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    global data
    logger.info("url=" + page_url)

    video_urls = list()
    host = "https://dood.watch"

    label = scrapertools.find_single_match(data, 'type:"video/([^"]+)"')

    js_code = scrapertools.find_single_match(data, ("(function makePlay.*?;})"))
    js_code = re.sub(r"\+Date.now\(\)", '', js_code)
    js = js2py.eval_js(js_code)
    makeplay = js() + str(int(time.time()*1000))

    base_url = scrapertools.find_single_match(data, r"\$.get\('([^']+)'")
    data = httptools.downloadpage("%s%s" % (host, base_url), headers={"referer": page_url}).data
    data = re.sub(r'\s+', '', data)
    values = [("/", "1"), ("/", "Z"), ("@", "a")]
    for val in values:
        logger.debug(data)
        data = re.sub(val[0], val[1], data)
        data = base64.b64decode(data)

    url = data + makeplay + "|Referer=%s" % page_url
    video_urls.append(['%s [doodstream]' % label, url])

    return video_urls
