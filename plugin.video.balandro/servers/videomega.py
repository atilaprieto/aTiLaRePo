# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger

def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    page_url = page_url.replace('videomega.co/e/', 'videomega.co/d/')
    if 'videomega.co/d/' not in page_url: page_url = page_url.replace('videomega.co/', 'videomega.co/d/')

    headers = {'Referer': page_url.replace('videomega.co/d/', 'videomega.co/')}
    data = httptools.downloadpage(page_url, headers=headers).data
    # ~ logger.debug(data)
    
    tn = scrapertools.find_single_match(data, "tnaketalikom\s*=\s*document\.getElementById\('([^']+)")
    if not tn: tn = scrapertools.find_single_match(data, 'tnaketalikom\s*=\s*document\.getElementById\("([^"]+)')
    bb = scrapertools.find_single_match(data, "bigbangass\s*=\s*document\.getElementById\('([^']+)")
    if not bb: bb = scrapertools.find_single_match(data, 'bigbangass\s*=\s*document\.getElementById\("([^"]+)')
    fo = scrapertools.find_single_match(data, "fuckoff\s*=\s*document\.getElementById\('([^']+)")
    if not fo: fo = scrapertools.find_single_match(data, 'fuckoff\s*=\s*document\.getElementById\("([^"]+)')
    if not tn or not bb or not fo: return video_urls

    tn = scrapertools.find_single_match(data, 'href="([^"]+)" id="%s"' % tn)
    bb = scrapertools.find_single_match(data, 'href="([^"]+)" id="%s"' % bb)
    fo = scrapertools.find_single_match(data, 'href="([^"]+)" id="%s"' % fo)
    if not tn or not bb or not fo: return video_urls

    url = 'https://www.videomega.co/streamurl/'+bb+'/'
    post = 'myreason=' + tn + '&saveme=' + fo
    headers = {'Referer': page_url, 'Content-Type': 'application/x-www-form-urlencoded'}
    url2 = httptools.downloadpage(url, post=post, headers=headers).data.strip()
    # ~ logger.debug(data)
    if url2.startswith('http'):
        headers = {'Referer': url}
        data = httptools.downloadpage(url2, headers=headers).data
        # ~ logger.debug(data)
        
        src = scrapertools.find_single_match(data, '<source src="([^"]+)')
        if src:
            video_urls.append(['mp4', src])

    return video_urls
