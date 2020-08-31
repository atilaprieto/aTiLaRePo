# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    
    # ~ data = httptools.downloadpage(page_url).data
    # ~ data = httptools.downloadpage(page_url, headers={'Referer': page_url.replace('evoload.io/e/', 'evoload.io/f/')}).data
    # ~ logger.debug(data)
    
    return video_urls
