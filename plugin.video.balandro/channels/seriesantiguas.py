# -*- coding: utf-8 -*-

import re

from platformcode import logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www.seriesantiguas.com/'


def mainlist(item):
    return mainlist_series(item)

def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host ))

    itemlist.append(item.clone( title = 'Novedades', action = 'list_all', url = host + 'search/label/ESTRENO' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'search/label/POPULARES' ))

    itemlist.append(item.clone( title = "Las de los 80's", action = 'list_all', url = host + 'search/label/80s' ))
    itemlist.append(item.clone( title = "Las de los 90's", action = 'list_all', url = host + 'search/label/90s' ))
    itemlist.append(item.clone( title = "Las de los 00's", action = 'list_all', url = host + 'search/label/00s' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, "<div class='post hentry'>(.*?)</h2>")

    num_matches = len(matches)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, "<img alt='(.*?)'")
        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')
        year = '-'

        itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, 
                                    contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if num_matches >= 6:
        patron = "<a class='blog-pager-older-link'"
        next_page = scrapertools.find_single_match(data,  patron + '.*?href="(.*?)"')

        if next_page:
            next_page = next_page.replace('&max-results=6', '&max-results=20')

            itemlist.append(item.clone (url = next_page, title = '>> Página siguiente', action = 'list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = "<div class='post-body entry-content'>.*?title=.*?"
    url_serie = scrapertools.find_single_match(data, patron + '<a href="(.*?)"')

    data = httptools.downloadpage(url_serie).data

    bloque = scrapertools.find_single_match(data, '>Temporadas<(.*?)</ul></li>')
    matches = scrapertools.find_multiple_matches(bloque, "<a href='(.*?)'>Temp (.*?)</a>")

    # averiguar cuantas temporadas hay
    tot_temp = 0

    for url, numtempo in matches:
        tot_temp += 1
        if tot_temp > 1: break

    for url, numtempo in matches:
        title = 'Temporada ' + numtempo

        if tot_temp == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&'), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.url = url
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist


        itemlist.append(item.clone( action = 'episodios', title = title, url = url, contentType = 'season', contentSeason = numtempo, page = 0 ))

    tmdb.set_infoLabels(itemlist)

    return itemlist

def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    perpage = 50

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, "<div class='post hentry'>(.*?)</h2>")

    for epis in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(epis, '<a href="([^"]+)"')

        episode = scrapertools.find_single_match(epis, "<img alt=.*?Temporada.*?x (.*?)'")
        episode = episode.replace(')', '')

        if not url or not episode: continue

        title = scrapertools.find_single_match(epis, "<img alt='(.*?)'")
        title = title.split('(')[0]
        title = title.strip()

        title = str(item.contentSeason) + 'x' + episode + ' ' + title

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, contentType = 'episode', contentEpisodeNumber = episode ))

        if len(itemlist) >= perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if len(matches) > (item.page + 1) * perpage:
        itemlist.append(item.clone( title=">> Página siguiente", action="episodios", page=item.page + 1, text_color='coral' ))

    return itemlist

def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    # ~ logger.debug(data)

    bloque = scrapertools.find_single_match(data, "<div class='post-body entry-content'>(.*?)<div class='post-footer'>")
    matches = scrapertools.find_multiple_matches(bloque, '<iframe.*?src="(.*?)"')

    for url in matches:
        if url.startswith('//'): url = 'https:' + url
        url = url.replace('&amp;', '&')

        servidor = servertools.get_server_from_url(url)
        url = servertools.normalize_url(servidor, url)

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = 'Lat' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.url = host + '/search/?q=' + texto.replace(" ", "+")
       return list_all(item)
    except:
       import sys
       for line in sys.exc_info():
           logger.error("%s" % line)
       return []
