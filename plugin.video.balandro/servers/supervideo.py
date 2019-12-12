# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger
import urllib

def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data
    # ~ logger.debug(data)

    if 'download_video(' not in data:
        post = {
            'op': scrapertools.find_single_match(data, '<input type="hidden" name="op" value="([^"]+)'),
            'usr_login': scrapertools.find_single_match(data, '<input type="hidden" name="usr_login" value="([^"]+)'),
            'id': scrapertools.find_single_match(data, '<input type="hidden" name="id" value="([^"]+)'),
            'fname': scrapertools.find_single_match(data, '<input type="hidden" name="fname" value="([^"]+)'),
            'referer': scrapertools.find_single_match(data, '<input type="hidden" name="referer" value="([^"]+)'),
            'hash': scrapertools.find_single_match(data, '<input type="hidden" name="hash" value="([^"]+)'),
        }
        if post['id'] and post['hash']:
            data = httptools.downloadpage(page_url, post=urllib.urlencode(post)).data
            # ~ logger.debug(data)

    matches = scrapertools.find_multiple_matches(data, "download_video\('([^']+)','([^']+)','([^']+)'\)\">([^<]+)</a></td><td>([^<]+)")
    for a, b, c, titulo, desc in matches:
        if b == 'l' and len(video_urls) > 1: continue # descartar low si ya hay original y normal
        
        data = httptools.downloadpage('https://supervideo.tv/dl?op=download_orig&id=%s&mode=%s&hash=%s' % (a, b, c)).data

        url = scrapertools.find_single_match(data, '<a href="([^"]+)">Direct Download Link</a>')
        if not url:
            post = {'op': 'download_orig', 'id': a, 'mode': b, 'hash': c}
            data = httptools.downloadpage('https://supervideo.tv/dl', post=urllib.urlencode(post)).data
            # ~ logger.debug(data)
            
            url = scrapertools.find_single_match(data, '<a href="([^"]+)">Direct Download Link</a>')

        if url:
            video_urls.append(["%s - %s" % (titulo.replace(' quality', ''), desc), url])

    video_urls.reverse() # calidad increscendo
    return video_urls
