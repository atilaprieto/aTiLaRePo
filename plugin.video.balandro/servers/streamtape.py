# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    page_url = page_url.replace('streamtape.com/e/', 'streamtape.com/v/')

    data = httptools.downloadpage(page_url).data
    # ~ logger.debug(data)
    
    url = scrapertools.find_single_match(data, '<div id="videolink"[^>]*>(.*?)</div>')
    if url:
        url += '&stream=1'
        if url.startswith('//'): url = 'https:' + url
        video_urls.append(['mp4', url])

    return video_urls

