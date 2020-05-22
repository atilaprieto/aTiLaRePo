# -*- coding: utf-8 -*-

from core import httptools, scrapertools, jsontools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    dom = 'https://feurl.com'
    vid = scrapertools.find_single_match(page_url, "/(?:v|f)/([A-z0-9_-]+)")
    if not vid: return video_urls

    post = {'r':'', 'd': dom.replace('https://', '')}
    data = httptools.downloadpage(dom+'/api/source/'+vid, post=post).data
    
    try:
        # ~ logger.debug(data)
        data = jsontools.load(data)
        # ~ logger.debug(data)
        
        if 'data' not in data or 'success' not in data: return 'Vídeo no encontrado'
        if not data['success']: return 'Vídeo no encontrado o eliminado'

        for videos in data['data']:
            if 'file' in videos:
                url = videos['file'] if videos['file'].startswith('http') else dom + videos['file']
                
                if '/redirector?' in url:
                    resp = httptools.downloadpage(url, follow_redirects=False)
                    if 'location' in resp.headers:
                        url = resp.headers['location']
                
                lbl = videos['label'] if 'label' in videos and videos['label'] else 'mp4'
                video_urls.append([lbl, url])
    except:
        pass

    return video_urls
