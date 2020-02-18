# -*- coding: utf-8 -*-
import re
from core import httptools
from core import scrapertools
from platformcode import logger
from lib import jsunpack


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).data
    packed = scrapertools.find_single_match(data, r'(eval.*?)</script>')
    unpacked = jsunpack.unpack(packed)
    url = scrapertools.find_single_match(unpacked, 'file:"([^"]+)"')
    video_urls.append(["[supervideo]", url])
    return video_urls

