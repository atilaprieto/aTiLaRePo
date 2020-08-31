# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger
from lib import jsunpack


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    
    data = httptools.downloadpage(page_url).data
    # ~ logger.debug(data)
    
    try:
        packed = scrapertools.find_single_match(data, "text/javascript'>(.*?)\s*</script>")
        if packed:
            data = jsunpack.unpack(packed)
            # ~ logger.debug(data)
    except:
        pass

    url = scrapertools.find_single_match(data, '\{src:\s*"([^"]+)')
    if url:
        video_urls.append(['m3u8', url])

    return video_urls
