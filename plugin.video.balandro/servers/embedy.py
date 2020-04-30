# -*- coding: utf-8 -*-

from core import httptools, scrapertools, jsontools
from platformcode import logger

def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    
    # ~ data = httptools.downloadpage(page_url).data
    # ~ logger.debug(data)

    vid = scrapertools.find_single_match(page_url, "embedy.cc/embed/([A-z0-9=]+)")

    data = httptools.downloadpage('https://embedy.cc/video.get/', post={'video':vid}, headers={'Referer': page_url}).data
    # ~ logger.debug(data)

    try:
        data_json = jsontools.load(data)
        for n in data_json['response']:
            for f in data_json['response'][n]['files']:
                video_urls.append([f, data_json['response'][n]['files'][f]])
    except:
        pass

    return video_urls
