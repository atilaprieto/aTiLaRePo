# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)

    page_url = page_url.replace('streamtape.com/v/', 'streamtape.com/e/')
    video_urls = get_aux(page_url)
    
    if len(video_urls) == 0:
        page_url = page_url.replace('streamtape.com/e/', 'streamtape.com/v/')
        video_urls = get_aux(page_url)

    return video_urls

def get_aux(page_url):
    video_urls = []
    
    data = httptools.downloadpage(page_url).data
    # ~ logger.debug(data)
    
    url = scrapertools.find_single_match(data, 'document\.getElementById\("videolink"\)\.innerHTML\s*=\s*"([^"]+)')
    if not url: url = scrapertools.find_single_match(data, '<div id="videolink"[^>]*>(.*?)</div>')
    if url:
        url += '&stream=1'
        if url.startswith('//'): url = 'https:' + url

        # ~ resp = httptools.downloadpage(url, headers={'Referer': page_url}, follow_redirects=False, only_headers=True)
        # ~ if 'location' in resp.headers: 
            # ~ url = resp.headers['location']

        video_urls.append(['mp4', url])

    return video_urls
