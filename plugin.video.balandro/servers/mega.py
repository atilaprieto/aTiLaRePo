# -*- coding: utf-8 -*-

from core import httptools, scrapertools, jsontools
from platformcode import logger, platformtools


def get_video_url(page_url, url_referer=''):
    page_url = page_url.replace('/embed/', '/embed#')
    page_url = page_url.replace('/file/', '/embed#')
    page_url = page_url.replace('/embed#', '/#!')
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    from lib.megaserver import Client
    c = Client(url=page_url, is_playing_fnc=platformtools.is_playing)
    files = c.get_files()
    # si hay mas de 5 archivos crea un playlist con todos
    # Esta función (la de la playlist) no va, hay que ojear megaserver/handler.py aunque la llamada este en client.py
    if len(files) > 5:
        media_url = c.get_play_list()
        video_urls.append([scrapertools.get_filename_from_url(media_url)[-4:] + " [mega]", media_url])
    else:
        for f in files:
            media_url = f["url"]
            video_urls.append([scrapertools.get_filename_from_url(media_url)[-4:] + " [mega]", media_url])

    return video_urls