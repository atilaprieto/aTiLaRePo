# -*- coding: utf-8 -*-
import re
from core import httptools
from core import scrapertools
from platformcode import logger


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    url= "https://txxx.com/api/videofile.php?video_id=%s&lifetime=864000" % page_url
    ref= "https://txxx.com/embed/%s/" % page_url
    headers = {'Referer': ref}
    data = httptools.downloadpage(url, headers=headers).data
    texto = scrapertools.find_single_match(data, '"video_url":"([^"]+)"')
    url = dec_url(texto)
    url = "https://txxx.com%s" % url
    url = httptools.downloadpage(url, only_headers=True).url
    video_urls.append(["[TXX]", url])
    return video_urls


def dec_url(txt):
    #truco del mendrugo
    # txt = txt.replace('\u0410', 'A').replace('\u0412', 'B').replace('\u0421', 'C').replace('\u0415', 'E').replace('\u041c', 'M').replace('~', '=').replace(',','/')
    txt = txt.decode('unicode-escape').encode('utf8')
    txt = txt.replace('А', 'A').replace('В', 'B').replace('С', 'C').replace('Е', 'E').replace('М', 'M').replace('~', '=').replace(',','/')
    import base64
    url = base64.b64decode(txt)
    return url
