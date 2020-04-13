# -*- coding: utf-8 -*-
import re
from core import httptools
from core import scrapertools
from platformcode import logger
from lib import jsunpack


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    url = httptools.downloadpage(page_url).url
    data = httptools.downloadpage(url).data
    data = scrapertools.find_single_match(data, '<footer id="Footer" class="clearfix">(.*?)</html>')
    packed = scrapertools.find_single_match(data, r'(eval.*?)</script>')
    unpacked = jsunpack.unpack(packed)

    url = scrapertools.find_single_match(unpacked, '(https://streamz.cc/getlink.*?.dll)')
    url = httptools.downloadpage(url, follow_redirects=False).headers["location"]
    video_urls.append(["[streamz]", url])
    return video_urls

