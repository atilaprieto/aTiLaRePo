# -*- coding: utf-8 -*-

import re

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, jsontools


host = "https://www.xvideos.com/"

perpage = 30


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    if descartar_xxx: return itemlist
    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False:
            return itemlist

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host, page=0 ))

    itemlist.append(item.clone( title = 'Por canal', action = 'canales', url = host + 'channels-index', page=0 ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias' ))

    itemlist.append(item.clone( title = 'Por estrella', action = 'list_pornstars', url = host + 'pornstars-index', page=0 ))

    itemlist.append(item.clone( title = 'Buscar vídeo ...', action = 'search', search_type = 'movie' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)
    patron = '<div class="thumb"><a href="([^"]+)".*?data-src="([^"]+)".*?title="([^"]+)"'

    matches = re.compile(patron).findall(data)

    for url, thumb, title in matches:
        itemlist.append(item.clone( action = 'findvideos', url = url if url.startswith('http') else host[:-1] + url,
                                    title = title, thumbnail = thumb, contentType = 'movie', contentTitle = title ))

    if itemlist:
        patron = '<a href="([^"]+)" class="no-page next-page">'
        next_url = scrapertools.find_single_match(data, patron)

        if next_url:
            itemlist.append(item.clone( title = '>> Página siguiente', url = next_url if next_url.startswith('http') else host[:-1] + next_url,
                                        action = 'list_all', page = item.page + 1, text_color = 'coral' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    perpage = 250

    data = httptools.downloadpage(host + 'tags').data

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = '<li><a href="(/tags/[^"]+)"><b>([^<]+)'

    matches = re.compile(patron).findall(data)

    num_matches = len(matches)
    desde = item.page * perpage
    hasta = desde + perpage

    for url, title in matches[desde:hasta]:
        titulo = title.capitalize()

        itemlist.append(item.clone( action = 'list_all', url = url if url.startswith('http') else host[:-1] + url, title = titulo))

    if itemlist:
        if num_matches > hasta:
            itemlist.append(item.clone( title = '>> Página siguiente', page = item.page + 1, action = 'categorias', text_color='coral' ))

    return itemlist


def list_pornstars(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)
    patron = '<li><a href="([^"]+)" class="btn btn-default">\s*([^<]+)'
    matches = re.compile(patron).findall(data)

    for url, title in matches:
        itemlist.append(item.clone( action = 'pornstars', url = url if url.startswith('http') else host[:-1] + url, title = title))

    return itemlist


def pornstars(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)
    patron = r'xv.thumbs.replaceThumbUrl\(\'<img src="([^"]+)".*?<a href="([^"]+)">([^<]+)'
    matches = re.compile(patron).findall(data)
    for thumb, url, title in matches:
        itemlist.append(item.clone( action = 'list_all', url = url if url.startswith('http') else host[:-1] + url,
                                    title = title, thumbnail = thumb ))

    if itemlist:
        patron = '<a href="([^"]+)" class="no-page next-page">'
        next_url = scrapertools.find_single_match(data, patron)
        if next_url:
            itemlist.append(item.clone( title = '>> Página siguiente', url = next_url if next_url.startswith('http') else host[:-1] + next_url,
                                        action = 'pornstars', page = item.page + 1, text_color = 'coral' ))

    return itemlist

def canales(item):
    logger.info()
    itemlist = []
    
    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)
    patron = '<li><a href="(\/channels[^"]+)">([^<|\d+]+)'
    matches = re.compile(patron).findall(data)
    for url, title in matches:
        itemlist.append(item.clone( action = 'list_channels', url = url if url.startswith('http') else host[:-1] + url, title = title))

    return sorted(itemlist, key=lambda x: x.title)


def list_channels(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)
    patron = '<div class="thumb-inside"><div class="thumb"><a href="([^"]+)">.*?xv.thumbs.replaceThumbUrl\(\'<img src="([^"]+)".*?span class="profile-name">([^<]+)'
    matches = re.compile(patron).findall(data)

    for url, thumb, title in matches:
        url = url if url.startswith('http') else host[:-1] + url
        url = url + 'videos/new/0' if url.endswith('/') else url + '/videos/new/0'

        itemlist.append(item.clone( action = 'list_all', url = url, title = title, thumbnail = thumb ))

    if itemlist:
        patron = '<li class="page_next"><a href="([^"]+)'
        next_url = scrapertools.find_single_match(data, patron)
        if next_url:
            next_url = next_url.replace('&amp;', '&')

            itemlist.append(item.clone( title = '>> Página siguiente', url = next_url if next_url.startswith('http') else host[:-1] + next_url,
                                        action = 'list_channels', page = item.page + 1, text_color = 'coral' ))

    return itemlist


def list_channels_categories(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = '<div class="floatLeft"><h2>([^<]+)</h2></div>'
    patron += '<div class="floatRight"><a class="seeAllButton greyButton light" href="([^"]+)'
    matches = re.compile(patron).findall(data)

    for title, url in matches:
        if 'premium' in title: continue

        itemlist.append(item.clone( action = 'list_channels_videos', url = url if url.startswith('http') else host[:-1] + url, title = title))

    return itemlist


def list_channels_videos(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    url = item.url + 'videos/best/' if item.url.endswith('/') else item.url + '/videos/best/'

    data = httptools.downloadpage(url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<ul class="videos row-5-thumbs videosGridWrapper" id="showAllChanelVideos">(.*?)<\/ul>')
    patron = '<a href="([^"]+)" title="([^"]+)"class="[^"]+"[^<]+<imgsrc="([^"]+)"data-thumb_url = "([^"]+)'
    matches = re.compile(patron).findall(bloque)

    for url, title, thumb, thumb2 in matches:
        itemlist.append(item.clone( action = 'findvideos', url = url if url.startswith('http') else host[:-1] + url,
                                    title = title, thumbnail = thumb if not 'base64' else thumb2, contentType = 'movie', contentTitle = title ))

    if itemlist:
        patron = '<li class="page_next"><a href="([^"]+)'
        next_url = scrapertools.find_single_match(data, patron)
        if next_url:
            next_url = next_url.replace('&amp;', '&')

            itemlist.append(item.clone( title = '>> Página siguiente', url = next_url if next_url.startswith('http') else host[:-1] + next_url,
                                        action = 'list_channels_videos', page = item.page + 1, text_color = 'coral' ))

    return itemlist

def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    m3u8url = re.findall(r"html5player\.setVideoHLS\('([^']+)'", data)[0]
    data = httptools.downloadpage(m3u8url).data

    matches = re.compile('(?i)name="([^"]+)"\s*(.*?m3u8)').findall(data)
    for calidad, url in matches:
        if not calidad or not url: continue
        url = m3u8url.replace("hls.m3u8", url)

        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', quality = calidad, url = url, language = 'VO' ))

    return sorted(itemlist, key=lambda i: i.quality)


def search(item, texto):
    logger.info()
    try:
        item.url =  host + "?k=%s" % (texto.replace(" ", "%20"))
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
