# -*- coding: utf-8 -*-

import re

from platformcode import logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://www.megadede.la/'


# ~ def item_configurar_proxies(item):
    # ~ plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    # ~ plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    # ~ return item.clone( title = 'Configurar proxies a usar ...', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )

# ~ def configurar_proxies(item):
    # ~ from core import proxytools
    # ~ return proxytools.configurar_proxies_canal(item.channel, host)


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series' ))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all' ))

    # ~ itemlist.append(item_configurar_proxies(item))
    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas', search_type = 'movie', page=0 ))

    itemlist.append(item.clone( title = 'Películas al azar', action = 'list_all', url = host + 'random', search_type = 'movie', page=0 ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie', page=0 ))

    itemlist.append(item.clone( title = 'Por año', action = 'anios', url = host + 'peliculas', search_type = 'movie', page=0 ))

    itemlist.append(item.clone( title = 'Por país', action = 'paises', url = host + 'peliculas', search_type = 'movie', page=0 ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'alfabetico', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    # ~ itemlist.append(item_configurar_proxies(item))
    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'tv-series', search_type = 'tvshow', page=0 ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow', page=0 ))

    itemlist.append(item.clone( title = 'Por año', action = 'anios', url = host + 'tv-series', search_type = 'tvshow', page=0 ))

    itemlist.append(item.clone( title = 'Por país', action = 'paises', url = host + 'tv-series', search_type = 'tvshow', page=0 ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    # ~ itemlist.append(item_configurar_proxies(item))
    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    if item.search_type == 'movie':
        url_genres = host + 'peliculas'
    else:
        url_genres = host + 'tv-series'

    data = httptools.downloadpage(url_genres).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<li class="cat-item cat-item-\d+"><a href="([^"]+)".*?>([^<]+)').findall(data)

    for url, title in matches:
        itemlist.append(item.clone( action = "list_all", title = title, url = url, page = item.page ))

    return sorted(itemlist, key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    if item.search_type == 'movie':
       tope = 1960
    else:
       tope = 2008

    for x in range(current_year, tope, -1):
        itemlist.append(item.clone( title=str(x), url= host + 'years/' + str(x), action='list_all' ))

    return itemlist


def paises(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)
    matches = re.compile('<li><a href="([^"]+)">([a-z|A-Z]+)').findall(data)

    for url, title in matches:
        if title.lower() == "united": title = "United Kingdom"
        itemlist.append(item.clone( action = "list_all", title = title, url = url ))

    return sorted(itemlist, key=lambda x: x.title)


def alfabetico(item):
    logger.info()
    itemlist = []

    url_letra = host + '?ap='

    for letra in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ#':
        if letra == '#': url = url_letra + 'numeric'
        else: url = url_letra + letra

        itemlist.append(item.clone( title = letra, action = 'list_all', url = url, page=0 ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    raise_weberror = False if '/years/' in item.url else True

    data = httptools.downloadpage(item.url, raise_weberror=raise_weberror).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if item.search_type == "movie" or item.search_type == "all":
        movies_pattern = '<div class="item"><a href="([^"]+)"><div class="item-flip"><div class="item-inner">'
        movies_pattern += '<img src="([^"]+)" alt="([^"]+)"><\/div><div class="item-details"><div class="item-details-inner">'
        movies_pattern += '<h2 class="movie-title">[^<]+<\/h2><p class="movie-description">([^<]+).*?<span class="movie-date">(\d+)'

        sufijo = '' if item.search_type != 'all' else 'movie'

        for url, thumb, title, info, year in re.compile(movies_pattern).findall(data):
            if not url or not title: continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                            contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': info} ))

    if item.search_type == "tvshow" or item.search_type == "all":
        series_pattern = '<div class="item"><a href="([^"]+)"><div class="item-flip"><div class="item-inner"><span class="item-tv">TV<i>'
        series_pattern += '<\/i><\/span><img src="([^"]+)" alt="([^"]+)"><\/div><div class="item-details"><div class="item-details-inner">'
        series_pattern += '<h2 class="movie-title">[^<]+<\/h2><p class="movie-description">([^<]+).*?<span class="movie-date">(\d+)'

        sufijo = '' if item.search_type != 'all' else 'tvshow'

        for url, thumb, title, info, year in re.compile(series_pattern).findall(data):
            if not url or not title: continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year, 'plot': info} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_url = scrapertools.find_single_match(data, '''<a class='arrow_pag' href="([^"]+)"''')
        if not len(next_url) > 0: next_url = scrapertools.find_single_match(data, '<link rel="next" href="([^"]+)" />')
        if next_url:
            itemlist.append(item.clone( title='>> Página siguiente', url=next_url, page=item.page + 1, action='list_all',
                                        contentType=item.search_type, text_color='coral' ))

    return itemlist


def temporadas (item):
    logger.info()
    itemlist = []

    if not item.url.startswith("http"): item.url = host[:-1] + item.url
    data = httptools.downloadpage(item.url).data
    matches = re.compile(r"openload(\d+)_(\d+)").findall(data)

    temporadas = []
    for season, episode in matches:
        if season not in temporadas: temporadas.append(season)

    for tempo in temporadas:
        title = "Temporada " + tempo

        if len(temporadas) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&'), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = tempo, page = 0 ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios (item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    perpage = 50

    data = httptools.downloadpage(item.url).data
    matches = re.compile("""openload""" + item.contentSeason + """_(\d+) span"\)\.append\("<iframe width='100%' height='313px' src='([^']+)""" ).findall(data)

    for episode, url in matches[item.page * perpage:]:
        title = str(item.contentSeason) + 'x' + str(episode) + ' ' + item.contentSerieName

        itemlist.append(item.clone( action='findvideos', url=url, title=title, 
                                    contentType = 'episode', contentEpisodeNumber = episode ))

        if len(itemlist) >= perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if len(matches) > ((item.page + 1) * perpage):
        itemlist.append(item.clone( title=">> Página siguiente", action="episodios", page=item.page + 1, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    if item.contentType != "episode":
        data = httptools.downloadpage(item.url).data
        matches = re.compile('<a class="blue" id="videoplayer\d+" title="([^"]+)" href="([^"]+)" title="([^"]+)"').findall(data)
        for server, url, quality in matches:
            itemlist.append(Item( channel = item.channel, action = 'play', title = '', quality=quality, url = url, server = server))
    else:
        servidor = servertools.get_server_from_url(item.url)
        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = item.url, server=servidor))

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.url = host + '?s=' + texto
       return list_all(item)
    except:
       import sys
       for line in sys.exc_info():
           logger.error("%s" % line)
       return []
