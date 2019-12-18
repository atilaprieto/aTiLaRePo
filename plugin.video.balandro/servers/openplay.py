# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger, platformtools

def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data
    # ~ logger.debug(data)

    bloque = scrapertools.find_single_match(data, '"sources":\s*\[(.*?)\]')
    url = scrapertools.find_single_match(bloque, '"file":\s*"(http[^"]+)')

    if url:
        from lib.m3u8server import Client
        c = Client(url=url, is_playing_fnc=platformtools.is_playing)
        video_urls.append(['m3u8', c.get_file()])

    return video_urls
