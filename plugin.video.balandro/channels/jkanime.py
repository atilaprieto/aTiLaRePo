# -*- coding: utf-8 -*-

import os, re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb, jsontools


host = 'https://jkanime.net/'

perpage = 30


def mainlist(item):
    return mainlist_anime(item)


def mainlist_anime(item):
    logger.info()
    itemlist = []

    descartar_anime = config.get_setting('descartar_anime', default=False)

    if descartar_anime: return itemlist
    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False:
            return itemlist
    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host, search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Novedades', action = 'list_all', url = host, search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'alfabetico', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data
    patron = r'<li><a href="([^"]+)".*?">([^<]+)'
    matches = re.compile(patron).findall(data)

    search_type = item.search_type

    for url, title in matches:
        if title == "Peliculas": 
            search_type = "movie"

        itemlist.append(item.clone( action = "list_all", title = title, url = host[:-1] + url, search_type = search_type))

    return sorted(itemlist, key=lambda x: x.title)


def alfabetico(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    patron = 'li><a class="letra-link" href="([^"]+)".*?">([^<]+)'

    matches = re.compile(patron).findall(data)

    for url, title in matches:
        itemlist.append(item.clone( action = "list_all", title = title, url = host[:-1] + url))

    return sorted(itemlist, key=lambda x: x.title)


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    data = httptools.downloadpage(item.url).data

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)
    patron = '<h2 class="portada-title"><a title="([^"]+)" href="([^"]+)".*?<img src="([^"]+)"'

    matches = re.compile(patron).findall(data)
    num_matches = len(matches)

    for title, url, thumb in matches[item.page * perpage:]:
        if not url or not title: continue

        if item.search_type == "tvshow":
            itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb, 
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year':'-'} ))
        else:
            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                        contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    # Subpaginación interna y/o paginación de la web
    buscar_next = True
    if num_matches > perpage: # subpaginación interna dentro de la página si hay demasiados items
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title = '>> Página siguiente', page = item.page + 1, action = 'list_all', text_color = 'coral' ))
            buscar_next = False

    if buscar_next:
        if itemlist:
            patron = '<a class="text nav-next" href="([^"]+)"'
            next_url = scrapertools.find_single_match(data, patron)
            if next_url:
                itemlist.append(item.clone( title = '>> Página siguiente', url = next_url, action = 'list_all', page = 0, text_color = 'coral' ))

            
    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 1

    perpage = 50

    data = httptools.downloadpage(item.url).data
    item.id_serie = scrapertools.find_single_match(data, 'ajax/pagination_episodes\/(\d+)\/')
    url = "%sajax/pagination_episodes/%s/%s/" %(host, item.id_serie, str(item.page))
    data = httptools.downloadpage(url).data
    jdata = jsontools.load(data)

    for match in jdata:
        itemlist.append(item.clone( action='findvideos', url = item.url + str(match['number']), title = match['title'],
                                    contentType = 'episode', contentEpisodeNumber=match['number'] ))

        if len(itemlist) >= perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if len(itemlist) > (item.page + 1) * perpage:
        itemlist.append(item.clone( title=">> Página siguiente", action="episodios", page=item.page + 1, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []


    data = httptools.downloadpage(item.url).data

    # ~ if developer == True: logger.debug(data)
    patron = r'video\[\d+\] = \'<iframe.*?src="([^"]+)'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for url in matches:
        if not url: continue

        servidor = servertools.get_server_from_url(url)
        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if "jkanime.net/um.php" in item.url:
        data = httptools.downloadpage(item.url).data
        url_play = scrapertools.find_single_match(data, "swarmId: \'([^\']+)\'")
    elif "okru" in item.url or "fembed" in item.url or "mixdrop" in item.url:
        data = httptools.downloadpage(item.url).data
        url_play = scrapertools.find_single_match(data, '<iframe.*?src="([^"]+)"')
    else:
        url_play = item.url

    #logger.debug(url_play)    
    if not url_play.startswith("http"):
        url_play = "https:" + url_play
    if url_play:
        itemlist.append(item.clone(url = url_play.replace("\\/", "/")))

    return itemlist


def search(item, texto):
    logger.info()

    try:
        item.url = host + 'buscar/' + texto.replace(" ", "_")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

