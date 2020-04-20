# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data
    # ~ logger.debug(data)

    if '404 Not Found' in data or 'File is no longer available' in data:
        return 'El archivo ha sido eliminado o no existe'

    video_urls = get_sources(data)
    if len(video_urls) > 0: return video_urls

    post = {
        'op': scrapertools.find_single_match(data, '<input type="hidden" name="op" value="([^"]+)'),
        'usr_login': scrapertools.find_single_match(data, '<input type="hidden" name="usr_login" value="([^"]+)'),
        'id': scrapertools.find_single_match(data, '<input type="hidden" name="id" value="([^"]+)'),
        'fname': scrapertools.find_single_match(data, '<input type="hidden" name="fname" value="([^"]+)'),
        'referer': scrapertools.find_single_match(data, '<input type="hidden" name="referer" value="([^"]+)'),
        'hash': scrapertools.find_single_match(data, '<input type="hidden" name="hash" value="([^"]+)'),
        'imhuman': 'Proceed to video'
    }
    data = httptools.downloadpage(page_url, post=post, headers={'Referer': page_url}).data
    # ~ logger.debug(data)
    video_urls = get_sources(data)

    return video_urls

def get_sources(data):
    video_urls = []

    bloque = scrapertools.find_single_match(data, 'sources\s*:\s*\[(.*?)\]')
    matches = scrapertools.find_multiple_matches(bloque, '(http.*?)"')
    for videourl in matches:
        extension = scrapertools.get_filename_from_url(videourl)[-4:]
        video_urls.append([extension, videourl])

    return video_urls
