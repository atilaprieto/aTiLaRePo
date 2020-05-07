# -*- coding: utf-8 -*-

from core import httptools, scrapertools, jsontools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    if 'peertube.librelabucm.org/download/videos/' in page_url:
        video_urls.append(['mp4', page_url])
        return video_urls

    vid = scrapertools.find_single_match(page_url, '(?:watch|embed)/([A-z0-9\-]+)')
    if not vid: return video_urls

    try:
        data = httptools.downloadpage('https://peertube.librelabucm.org/api/v1/videos/' + vid).data
        # ~ logger.debug(data)

        data_json = jsontools.load(data)
        try:
            lista = sorted(data_json['files'], key=lambda x: x['resolution']['id'])
        except:
            lista = data_json['files']
        
        for vid in lista:
            if 'fileDownloadUrl' not in vid: continue
            url = vid['fileDownloadUrl']
            if url.startswith('/'): url = 'https://peertube.librelabucm.org' + url

            try: 
                lbl = ['resolution']['label']
            except:
                lbl = None
            if not lbl: lbl = 'mp4'

            video_urls.append([lbl, url])
    except:
        pass

    return video_urls
