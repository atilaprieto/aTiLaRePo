# -*- coding: utf-8 -*-

from core import httptools, scrapertools, jsontools
from platformcode import logger

def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    vid = scrapertools.find_single_match(page_url, 'jetload.net/(?:e|p|#!/v|#!/d)/([A-z0-9]+)')
    if not vid: return video_urls

    url = 'https://jetload.net/api/fetch/' + vid
    data = httptools.downloadpage(url, headers={'Referer': page_url}).data
    # ~ logger.debug(data)

    if 'client_not_paired' in data:
        return 'Este servidor solamente funciona si se hace "pairing" desde un navegador web. Visita https://JLPair.NET y pulsa "Pair Now!". Durante 3 horas y desde la misma IP podrás acceder a los enlaces de Jetload desde Kodi.'
    else:
        try:
            data_json = jsontools.load(data)
            if 'src' in data_json and 'src' in data_json['src']:
                lbl = data_json['src']['type'] if 'type' in data_json['src'] and data_json['src']['type'] else 'mp4'
                video_urls.append([lbl, data_json['src']['src']])
        except:
            pass

    return video_urls
