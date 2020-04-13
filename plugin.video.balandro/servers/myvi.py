# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger
import urllib

def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    
    data = httptools.downloadpage(page_url).data
    # ~ logger.debug(data)

    data = scrapertools.find_single_match(data, 'CreatePlayer\("([^"]+)')
    if not data: return video_urls

    data = urllib.unquote(data)
    # ~ logger.debug(data)
    
    bloques = data.split('\u0026')
    # ~ logger.debug(bloques)
    
    if bloques[0].startswith('v=//'):
        video_urls.append(['mp4', bloques[0].replace('v=', 'https:')])
    elif bloques[0].startswith('v=http'):
        video_urls.append(['mp4', bloques[0].replace('v=', '')])

    return video_urls
