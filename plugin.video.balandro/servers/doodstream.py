# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger
import base64, random, time

def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    
    page_url = page_url.replace('/d/','/e/')
    # ~ page_url = page_url.replace('doodstream.com/','dood.watch/')

    data = httptools.downloadpage(page_url).data
    # ~ logger.debug(data)
    
    url = scrapertools.find_single_match(data, "\$\.get\('([^']+)")
    if url:
        headers = {'Referer': page_url}
        if url.startswith('/'): url = 'https://doodstream.com' + url
        # ~ if url.startswith('/'): url = 'https://dood.watch' + url
        data2 = httptools.downloadpage(url, headers=headers).data
        # ~ logger.debug(data2)
        if not data2: return itemlist
        
        data2 = data2.replace('\n', '')
        data2 = base64.b64decode(data2.replace('/', '1'))
        data2 = base64.b64decode(data2.replace('/', 'Z'))
        data2 = base64.b64decode(data2.replace('@', 'a'))
        # ~ logger.debug(data2)
        
        token = scrapertools.find_single_match(data, 'return a\+"([^"]+)')
        if not token: return itemlist
        a = ''.join([random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789') for i in range(10)])
        a += token + str(int(time.time()*1000))
        
        url = data2 + a
        # ~ video_urls.append(['mp4', data2 + a])
        video_urls.append(['mp4', data2 + a +'|Referer=https://doodstream.com/'])
        # ~ video_urls.append(['mp4', data2 + a +'|Referer=https://dood.watch/'])

    return video_urls
