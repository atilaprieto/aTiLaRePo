# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger, platformtools
from lib import jsunpack

def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data
    # ~ logger.debug(data)

    packed = scrapertools.find_multiple_matches(data, "(?s)eval(.*?)\s*</script>")
    for pack in packed:
        try:
            data = jsunpack.unpack(pack)
        except:
            data = ''
        # ~ logger.debug(data)
        if 'sources:[' in data: break
    # ~ logger.debug(data)

    bloque = scrapertools.find_single_match(data, 'sources:\s*\[(.*?)\]')
    matches = scrapertools.find_multiple_matches(bloque, '\{file:"([^"]+)"([^}]*)')
    for url, extra in matches:
        lbl = scrapertools.find_single_match(extra, 'label:"([^"]+)')
        if not lbl: lbl = url[-4:]
        if lbl == '.mpd':
            if platformtools.is_mpd_enabled():
                video_urls.append([lbl, url, 0, '', True])
        else:
            video_urls.append([lbl, url])

    return video_urls
