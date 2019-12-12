# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger
from lib import jsunpack


def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data
    # ~ logger.debug(data)

    packed = scrapertools.find_single_match(data, "(eval.*?)</script>")
    if packed:
        data = jsunpack.unpack(packed)
        # ~ logger.info(data)

    data = scrapertools.find_single_match(data, 'sources:\s*\[(.*?)\]')
    
    matches = scrapertools.find_multiple_matches(data, '"label"\s*:\s*"([^"]+)",.*?"file"\s*:\s*"([^"]+)"')
    if matches:
        for lbl, url in matches:
            video_urls.append([lbl, url])
    else:
        matches = scrapertools.find_multiple_matches(data, '"file"\s*:\s*"([^"]+)"')
        for url in matches:
            video_urls.append(['mp4', url])

    return video_urls
