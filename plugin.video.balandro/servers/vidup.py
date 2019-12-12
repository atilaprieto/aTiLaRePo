# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger
import urllib


def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    headers = {"Referer":page_url}
    url = httptools.downloadpage(page_url, follow_redirects=False, headers=headers, only_headers=True).headers.get("location", "")
    if not url: return 'Fichero no encontrado'

    post = {}
    post = urllib.urlencode(post)
    data = httptools.downloadpage("https://vidup.io/api/serve/video/" + scrapertools.find_single_match(url, "embed.([A-z0-9]+)"), post=post).data

    bloque = scrapertools.find_single_match(data, 'qualities":\{(.*?)\}')
    matches = scrapertools.find_multiple_matches(bloque, '"([^"]+)":"([^"]+)')
    for res, media_url in matches:
        video_urls.append(
            [scrapertools.get_filename_from_url(media_url)[-4:] + " (" + res + ")", media_url])

    video_urls.reverse()

    return video_urls
