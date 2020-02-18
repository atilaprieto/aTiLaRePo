# -*- coding: utf-8 -*-

from core import httptools
from core import scrapertools
from platformcode import logger




def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    server = scrapertools.find_single_match(page_url, 'https://www.([A-z0-9-]+).com')
    data = httptools.downloadpage(page_url).data
    data = scrapertools.find_single_match(data, '"files":(.*?)"quality"')
    patron  = '"([lh])q":"([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for quality, scrapedurl in matches:
        url =  scrapedurl.replace("\/", "/")
        if "l" in quality: quality = "360p"
        if "h" in quality: quality = "720p"
        video_urls.append(["[%s] %s" %(server,quality), url])
    return video_urls