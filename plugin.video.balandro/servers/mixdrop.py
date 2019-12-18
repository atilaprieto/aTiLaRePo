# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger
from lib import jsunpack

def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    headers = {'Referer': page_url.replace('mixdrop.co/e/', 'mixdrop.co/f/')}
    data = httptools.downloadpage(page_url, headers=headers).data
    # ~ logger.debug(data)

    packed = scrapertools.find_multiple_matches(data, "(?s)eval(.*?)\s*</script>")
    for pack in packed:
        try:
            data = jsunpack.unpack(pack)
        except:
            data = ''
        # ~ logger.debug(data)
        if 'MDCore.vsrc=' in data or 'MDCore.vsr=' in data: break

    url = scrapertools.find_single_match(data, 'MDCore\.vsrc="([^"]+)')
    if not url: url = scrapertools.find_single_match(data, 'MDCore\.vsr="([^"]+)')
    if url:
        if url.startswith('//'): url = 'https:' + url
        video_urls.append(["mp4", url])

    return video_urls
