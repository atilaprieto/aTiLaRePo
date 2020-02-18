# -*- coding: utf-8 -*-
import re
from core import httptools
from core import scrapertools
from platformcode import logger



def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    url = "https://www.tubeon.com/player_config_json/?vid=%s&aid=0&domain_id=0&embed=0&ref=null&check_speed=0" %page_url
    data = httptools.downloadpage(url).data
    data = scrapertools.find_single_match(data, '"files":(.*?)"quality"')
    patron  = '"([lh])q":"([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for quality, scrapedurl in matches:
        url =  scrapedurl.replace("\/", "/")
        if "l" in quality: quality = "360"
        if "h" in quality: quality = "720"
        video_urls.append(["[tubeon] %s" %quality, url])
    return video_urls

