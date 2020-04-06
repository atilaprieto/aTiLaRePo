# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector hclips By Alfa development Group
# --------------------------------------------------------

from core import httptools
from core import scrapertools
from platformcode import logger, config


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global data
    data = httptools.downloadpage(page_url).data
    if "<h2>WE ARE SORRY</h2>" in data or '<title>404 Not Found</title>' in data:
        return False, config.get_localized_string(70449) % "hclips"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []
    id = scrapertools.find_single_match(page_url, r"embed/([0-9]+)")
    url = "https://hclips.com/api/videofile.php?video_id=%s&lifetime=8640000" % id
    headers = {'Referer': page_url}
    data = httptools.downloadpage(url, headers=headers).data
    texto = scrapertools.find_single_match(data, 'video_url":"([^"]+)"')
    url = dec_url(texto)
    url = "https://hclips.com%s" % url
    media_url = httptools.downloadpage(url, only_headers=True).url
    video_urls.append(["[hclips]", media_url])
    return video_urls


def dec_url(txt):
    #truco del mendrugo
    # txt = txt.replace('\u0410', 'A').replace('\u0412', 'B').replace('\u0421', 'C').replace('\u0415', 'E').replace('\u041c', 'M').replace('~', '=').replace(',','/')
    txt = txt.decode('unicode-escape').encode('utf8')
    txt = txt.replace('А', 'A').replace('В', 'B').replace('С', 'C').replace('Е', 'E').replace('М', 'M').replace('~', '=').replace(',','/')
    import base64
    url = base64.b64decode(txt)
    return url

