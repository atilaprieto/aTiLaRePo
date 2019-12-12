# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger
from lib import jsunpack


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    # ~ if not page_url.endswith('.html'): page_url += '.html'

    data = httptools.downloadpage(page_url).data
    # ~ logger.debug(data)

    packed = scrapertools.find_single_match(data, "<script type=[\"']text/javascript[\"']>(eval.*?)</script>")
    if packed:
        data = jsunpack.unpack(packed)
        # ~ logger.info(data)

    bloque = scrapertools.find_single_match(data, 'sources:\s*\[(.*?)\]')
    matches = scrapertools.find_multiple_matches(bloque, '(http.*?)"')
    for videourl in matches:
        extension = scrapertools.get_filename_from_url(videourl)[-4:]
        video_urls.append([extension, videourl])


    bloque = scrapertools.find_single_match(data, 'player\.updateSrc\(\[(.*?)\]')
    matches = scrapertools.find_multiple_matches(bloque, 'src: "([^"]+)".*?, res: (\d+)')
    for url, res in sorted(matches, key=lambda x: int(x[1])):
        video_urls.append([res, url])

    return video_urls
