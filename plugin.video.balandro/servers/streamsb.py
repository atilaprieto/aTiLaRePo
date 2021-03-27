# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger
from lib import jsunpack


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    if '404 Not Found' in data or 'File Not Found' in data or 'File is no longer available' in data:
        return 'El fichero no existe o ha sido borrado'

    packed = scrapertools.find_single_match(data, r"'text/javascript'>(eval.*?)\n")
    unpacked = jsunpack.unpack(packed)

    video_srcs = scrapertools.find_single_match(unpacked, "sources:\[[^\]]+\]")
    video_info = scrapertools.find_multiple_matches(video_srcs, r'{(file:.*?)}')

    try:
        sub = scrapertools.find_single_match(unpacked, r'{file:"([^"]+)",label:"[^"]+",kind:"captions"')
    except:
        sub = ''

    for info in video_info:
        url = scrapertools.find_single_match(info, r'file:"([^"]+)"')

        if url:
            if url == sub: continue

            extension = scrapertools.get_filename_from_url(url)[-4:]
            if extension in ('.png`', '.jpg'): continue

            if extension == '.mpd':
                video_urls.append(['mpd', url])
            else:
                video_urls.append([sub, url])

    return video_urls
