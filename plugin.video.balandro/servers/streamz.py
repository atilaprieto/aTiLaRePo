# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger
from lib import jsunpack

def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data
    # ~ logger.debug(data)
    
    packed = scrapertools.find_single_match(data, "function\(p,a,c,k.*?</script>")
    if packed:
        unpacked = jsunpack.unpack(packed)
        # ~ logger.info(unpacked)
        url = scrapertools.find_single_match(unpacked.replace("\\'", "'"), "src:'([^']+)")
        if url and url.startswith('http'):
            url = httptools.downloadpage(url, headers={'Referer': page_url}, follow_redirects=False, only_headers=True).headers.get('location', '')
            if url: 
                if '/issue.mp4' in url: return 'El vídeo no está disponible en este momento'
                video_urls.append(['mp4', url])

    return video_urls
