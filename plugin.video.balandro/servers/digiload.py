# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger

def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    vid = scrapertools.find_single_match(page_url, "(?:e|f)/([A-z0-9_-]+)")
    if not vid: return video_urls
    page_url = 'https://digiload.live/player/e/' + vid
    
    data = httptools.downloadpage(page_url).data
    # ~ logger.debug(data)
    
    url = scrapertools.find_single_match(data, ' data-file="([^"]+)')
    if not url:
		url = scrapertools.find_single_match(data, '"file": "([^"]+)')

    if url:
        video_urls.append(['mp4', url])

    return video_urls
