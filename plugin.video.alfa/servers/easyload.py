# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector anonfile By Alfa development Group
# --------------------------------------------------------

from core import httptools
from core import jsontools
from platformcode import logger
from bs4 import BeautifulSoup

data = ""

def test_video_exists(page_url):
    global data
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url)
    if not data.sucess:
        return False, "[easyload] El fichero no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    video_urls = list()

    soup = BeautifulSoup(data.data, "html5lib")
    embed_data = soup.find("fileembed-component")["v-bind:data"]
    strm_data = jsontools.load(embed_data)["streams"]

    for strm in strm_data:
        src = list(strm_data[strm]["src"])
        t = '15'
        media_url = ''.join(chr(ord(src[n]) ^ ord(t[n % len(t)])) for n in range(len(src)))
        qlty = strm_data[strm]["resolution"]
        video_urls.append(['%sp [easyload]' % qlty, media_url])
    return video_urls
