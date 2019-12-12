# -*- coding: utf-8 -*-

from core import httptools, scrapertools, jsontools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    try:
		resp = httptools.downloadpage(page_url)
		# ~ logger.debug(resp.data)
		
		data = scrapertools.find_single_match(resp.data, "JSON\.parse\('(\[.*?\])'\)").replace('\\/', '/')
		# ~ logger.debug(data)

		data = jsontools.load(data)
		for video in sorted(data, key=lambda x: int(x['res'])):
			video_urls.append([video['label'], video['src']])

    except:
        pass

    return video_urls
