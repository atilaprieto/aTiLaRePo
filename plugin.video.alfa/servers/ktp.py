# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector vipporns By Alfa development Group
# --------------------------------------------------------
import re

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
        return False, "[ktplayer] El fichero no existe o ha sido borrado"

    global video_url, license_code
    # video_url = scrapertools.find_single_match(response.data, "video_url: '([^']+)'")
    license_code = scrapertools.find_single_match(response.data, "license_code: '([^']+)'")

    return True, ""

        # function/0/https://www.vipporns.com/get_file/4/d56c8b4bdbca83143a7b27dca85756c12296f1862e/6000/6090/6090.mp4/?embed=true
# function/0/https://www.submityourflicks.com/get_file/1/809ed209b418a110e4805e284243d4ee4589f3307e/16000/16269/16269.mp4/

def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(page_url).data
    if "video_url_text" in data:
        patron = '(?:video_url|video_alt_url|video_alt_url[0-9]*):\s*\'([^\']+)\'.*?'
        patron += '(?:video_url_text|video_alt_url_text|video_alt_url[0-9]*_text):\s*\'([^\']+)\''
    else:
        patron = 'video_url:\s*\'([^\']+)\'.*?'
        patron += 'postfix:\s*\'([^\']+)\''
    matches = re.compile(patron,re.DOTALL).findall(data)
    logger.debug(matches)
    for url,quality in matches:
        if not "?login" in url:
            if "function/" in url:
                url = decode(url, license_code)
            itemlist.append(['%s' %quality, url])
    logger.debug(quality + " : " + url)
    return itemlist

    # return [["[ktplayer]", decode(video_url, license_code)]]