# -*- coding: utf-8 -*-

from core import httptools, scrapertools, jsontools
from platformcode import logger
from lib import balandroresolver

def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []
    
    vid = scrapertools.find_single_match(page_url, "uptobox.com/(?:iframe/|)([A-z0-9]+)")
    if not vid: return video_urls
    data = httptools.downloadpage('https://uptostream.com/api/streaming/source/get?token=null&file_code='+vid).data
    matches = balandroresolver.decode_video_uptostream(data)
    for match in matches:
        lbl = match.get('label')
        url = match.get('src')
        video_urls.append([lbl, url])
    return video_urls

