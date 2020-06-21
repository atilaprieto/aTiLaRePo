# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger
from lib import jsunpack


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    page_url = page_url.replace('http://', 'https://').replace('://www.', '://')
    if 'embed-' not in page_url: page_url = page_url.replace('mp4upload.com/', 'www.mp4upload.com/embed-') + '.html'

    data = httptools.downloadpage(page_url).data
    # ~ logger.debug(data)

    url = scrapertools.find_single_match(data, 'player\.src\("([^"]+)')
    if not url:
        packed = scrapertools.find_single_match(data, "<script type=[\"']text/javascript[\"']>(eval.*?)</script>")
        if packed:
            unpacked = jsunpack.unpack(packed)
            # ~ logger.debug(unpacked)
            url = scrapertools.find_single_match(unpacked, 'player\.src\("([^"]+)')
            if not url: url = scrapertools.find_single_match(unpacked, 'src:"([^"]+)')

    if url:
        video_urls.append(['mp4', url])

    return video_urls
