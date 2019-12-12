# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger
from lib import jsunpack

def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data
    # ~ logger.debug(data)

    packed = scrapertools.find_multiple_matches(data, "(?s)eval(.*?)\s*</script>")
    for pack in packed:
        try:
            data = jsunpack.unpack(pack)
        except:
            data = ''
        # ~ logger.debug(data)
        if 'sources:[' in data: break

    bloque = scrapertools.find_single_match(data, 'sources:\s*\[(.*?)\]')
    matches = scrapertools.find_multiple_matches(bloque, '(http.*?)"')
    for url in matches:
        video_urls.append(['mp4', url])

    return video_urls
