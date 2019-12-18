# -*- coding: utf-8 -*-

from core import httptools
from core import scrapertools
from lib import jsunpack
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    data = httptools.downloadpage(page_url).data

    if 'Not Found' in data or 'File is no longer available' in data:
        return False, "[Datoporn] El archivo no existe o ha sido borrado"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).data
    media_urls = scrapertools.find_multiple_matches(data, 'src: "([^"]+)",.*?label: "([^"]+)"')
    if not media_urls:
        match = scrapertools.find_single_match(data, "<script type='text/javascript'>(eval.function.p,a,c,k,e,d..*?)</script>")
        try:
            data = jsunpack.unpack(match)
        except:
            pass
        media_urls = scrapertools.find_multiple_matches(data, 'file\:"([^"]+\.mp4)",label:"([^"]+)"')
    # Extrae la URL
    for media_url, res in media_urls:
        try:
            title = ".%s %s [datoporn]" % (media_url.rsplit('.', 1)[1], res)
        except:
            title = ".%s %s [datoporn]" % (media_url[-4:], res)
        video_urls.append([title, media_url])
    m3u8 = scrapertools.find_single_match(data, 'file\:"([^"]+\.m3u8)"')
    if not m3u8:
        m3u8 = str(scrapertools.find_multiple_matches(data, 'player.updateSrc\({src:.?"([^"]+\.m3u8)"')).replace("['", "").replace("']", "")
        calidades = ['720p']
    if m3u8:
        video_urls.insert(0, [".m3u8 720p [datoporn]" ,  m3u8])
    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))
    return video_urls


