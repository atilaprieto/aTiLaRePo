# -*- coding: utf-8 -*-

from core import httptools
from core import scrapertools
from platformcode import config, logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    response = httptools.downloadpage(page_url)
    if response.code == 404:
        return False, config.get_localized_string(70449) % "RapidVideo"
    if not response.data or "urlopen error [Errno 1]" in str(response.code):
        if config.is_xbmc():
            return False, config.get_localized_string(70302) % "RapidVideo"
        elif config.get_platform() == "plex":
            return False, config.get_localized_string(70303) % "RapidVideo"
        elif config.get_platform() == "mediaserver":
            return False, config.get_localized_string(70304) % "RapidVideo"
    if "Object not found" in response.data:
        return False, config.get_localized_string(70449) % "RapidVideo"
    if response.code == 500:
        return False, config.get_localized_string(70524) % "RapidVideo"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).data
    post = "confirm.x=77&confirm.y=76&block=1"
    if "Please click on this button to open this video" in data:
        data = httptools.downloadpage(page_url, post=post).data
    patron = 'https://www.rapidvideo.com/e/[^"]+'
    match = scrapertools.find_multiple_matches(data, patron)
    if match:
        for url1 in match:
            res = scrapertools.find_single_match(url1, '=(\w+)')
            data = httptools.downloadpage(url1).data
            if "Please click on this button to open this video" in data:
                data = httptools.downloadpage(url1, post=post).data
            url = scrapertools.find_single_match(data, 'source src="([^"]+)')
            ext = scrapertools.get_filename_from_url(url)[-4:]
            video_urls.append(['%s %s [rapidvideo]' % (ext, res), url])
    else:
        patron = 'src="([^"]+)" type="video/([^"]+)" label="([^"]+)"'
        match = scrapertools.find_multiple_matches(data, patron)
        if match:
            for url, ext, res in match:
                video_urls.append(['.%s %s [Rapidvideo]' % (ext, res), url])

    return video_urls
