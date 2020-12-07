# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger
import random, time

def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    
    if '/d/' in page_url:
        data = httptools.downloadpage(page_url).data
        # ~ logger.debug(data)
        aux = scrapertools.find_single_match(data, '<iframe src="/e/([^"]+)')
        if aux: page_url = 'https://doodstream.com/e/' + aux
        else: page_url = page_url.replace('/d/','/e/')

    page_url = page_url.replace('https://doodstream.com', 'https://dood.to')

    data = httptools.downloadpage(page_url).data
    # ~ logger.debug(data)
    
    url = scrapertools.find_single_match(data, "get\('(/pass_md5/[^']+)")
    token = scrapertools.find_single_match(data, '"?token=([^"&]+)')
    if url and token:
        headers = {'Referer': page_url}
        data2 = httptools.downloadpage('https://dood.to' + url, headers=headers).data
        # ~ logger.debug(data2)
        if not data2: return video_urls

        a = ''.join([random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789') for i in range(10)])
        a += '?token=' + token + '&expiry=' + str(int(time.time()*1000))
        
        video_urls.append(['mp4', data2 + a +'|Referer=https://doodstream.com/'])

    return video_urls
