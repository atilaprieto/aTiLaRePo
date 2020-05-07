# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector hclips By Alfa development Group
# --------------------------------------------------------
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

from core import httptools
from core import scrapertools
from platformcode import logger, config


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url).data
    if "<h2>WE ARE SORRY</h2>" in data or '<title>404 Not Found</title>' in data:
        return False, config.get_localized_string(70449) % "hdzog"
    global server, vid
    server = scrapertools.find_single_match(page_url, '([A-z0-9-]+).com')
    vid = scrapertools.find_single_match(page_url, r'(?:embed|videos)/([0-9]+)')
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []
    host= "https://%s.com" % server
    headers = {'Referer': page_url}
    post_url = '%s/sn4diyux.php' %host
    data = httptools.downloadpage(page_url).data
    patron = 'pC3:\'([^\']+)\',.*?'
    patron += '(?:"|)video_id(?:"|): (\d+),'
    info_b, info_a = scrapertools.find_single_match(data, patron)
    post = 'param=%s,%s' % (info_a, info_b)
    new_data = httptools.downloadpage(post_url, post=post, headers=headers).data
    texto = scrapertools.find_single_match(new_data, 'video_url":"([^"]+)"')
    url = dec_url(texto)
    media_urls = httptools.downloadpage(url, only_headers=True).url
    video_urls.append(["[%s]" %server, media_urls])
    return video_urls


def dec_url(txt):
    #truco del mendrugo
    if not PY3:
        txt = txt.decode('unicode-escape').encode('utf8')
    else:
        txt = txt.encode('utf8').decode('unicode-escape')
    txt = txt.replace('А', 'A').replace('В', 'B').replace('С', 'C').replace('Е', 'E').replace('М', 'M').replace('~', '=').replace(',','/')
    import base64
    url = base64.b64decode(txt)
    return url


