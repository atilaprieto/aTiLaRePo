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

    headers = {'Referer': page_url}
    post_url = 'https://hclips.com/sn4diyux.php'

    data = httptools.downloadpage(page_url).data
    patron = 'pC3:\'([^\']+)\',.*?'
    patron += '"video_id": (\d+),'
    info_b, info_a = scrapertools.find_single_match(data, patron)
    post = 'param=%s,%s' % (info_a, info_b)
    new_data = httptools.downloadpage(post_url, post=post, headers=headers).data
    texto = scrapertools.find_single_match(new_data, 'video_url":"([^"]+)"')

    url = dec_url(texto)
    media_url = httptools.downloadpage(url, only_headers=True).url

    # if not media_url.startswith('http'):
        # media_url = 'http:%s' % media_url
    video_urls.append(["[hclips]", media_url])

    return video_urls


def dec_url(txt):
    #truco del mendrugo
    txt = txt.decode('unicode-escape').encode('utf8')
    txt = txt.replace('А', 'A').replace('В', 'B').replace('С', 'C').replace('Е', 'E').replace('М', 'M').replace('~', '=').replace(',','/')
    import base64
    url = base64.b64decode(txt)
    return url
