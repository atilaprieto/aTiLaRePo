# -*- coding: utf-8 -*-

import os, re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb, jsontools


host = 'https://www.animefenix.com/'

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
    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'animes?page=1', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host + 'animes?estado[]=1', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por categorízación', action = 'categories', url = host + 'animes', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', url = host + 'animes', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', url = host + 'animes', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    data = httptools.downloadpage(item.url).data

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)
    patron = '<article class="serie-card"><div class="serie-card__information"><p>([^<]+)<\/p>'
    patron += '<\/div><figure class="image"><a href="([^"]+)" title="([^"]+)">'
    patron += '<img src="([^"]+)".*?<span class="tag year is-dark">(\d+)'

    matches = re.compile(patron).findall(data)

    for info, url, title, thumb, year in matches[item.page * perpage:]:
        if not url or not title: continue

        itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb, 
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year':year, 'plot': info} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    # Subpaginación interna y/o paginación de la web
    if '<a class="pagination-link" href="' in data:
        patron = '<a class="pagination-link" href="([^"]+)">Siguiente'
        next_url = scrapertools.find_single_match(data, patron)
        next_url = item.url.split("?")[0] + next_url
        itemlist.append(item.clone( title = '>> Página siguiente', url = next_url, action = 'list_all', page = 0, text_color = 'coral' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)
    data = scrapertools.find_single_match(data, r'<select name="[^"]+" id="genre_select" multiple="multiple">(.*?)<\/select>')
    patron = r'<option value="([^"]+)"\s*>([^<]+)'
    matches = re.compile(patron).findall(data)

    for genre_id, title in matches:
        url = "%s?genero[]=%s&order=default&page=1" % (item.url, genre_id)
        itemlist.append(item.clone( title = title, action = 'list_all', url = url ))

    return sorted(itemlist,key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)
    data = scrapertools.find_single_match(data, r'<select name="[^"]+" id="year_select" multiple="multiple">(.*?)<\/select>')
    patron = r'<option value="([^"]+)"\s*>([^<]+)'
    matches = re.compile(patron).findall(data)

    for anio, title in matches:
        url = "%s?year[]=%s&order=default&page=1" % (item.url, anio)
        itemlist.append(item.clone( title = title, action = 'list_all', url = url ))

    return sorted(itemlist,key=lambda x: x.title)


def categories(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)
    data = scrapertools.find_single_match(data, r'<select name="[^"]+" id="order_select"(.*?)<\/select>')
    patron = r'<option value="([^"]+)"\s*>([^<]+)'
    matches = re.compile(patron).findall(data)

    for categoria, title in matches:
        if title == "Calificación": continue
        url = "%s?order=%s&page=1" % (item.url, categoria)
        itemlist.append(item.clone( title = title, action = 'list_all', url = url ))

    return sorted(itemlist,key=lambda x: x.title)


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    perpage = 50

    data = httptools.downloadpage(item.url).data
    patron = '<a class="fa-play-circle d-inline-flex align-items-center is-rounded " href="([^"]+)".*?<span>([^<]+)'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, title in matches[item.page * perpage:]:
        try:
            episode = scrapertools.find_single_match(title, "Episodio.*?(\d+)")
        except:
            episode = 0

        itemlist.append(item.clone( action='findvideos', url = url, title = title,
                                    contentType = 'episode', contentEpisodeNumber=episode ))

        if len(itemlist) >= perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if len(matches) > ((item.page + 1) * perpage):
        itemlist.append(item.clone( title=">> Página siguiente", action="episodios", page=item.page + 1, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []


    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)
    # ~ if developer == True: logger.debug(data)

    patron = r"tabsArray\['\d+'\] = \".*?src='(?:\.\.|)([^']+)"
    matches = re.compile(patron, re.DOTALL).findall(data)

    for url in matches:
        if not url: continue

        servidor = servertools.get_server_from_url(url)

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url ))

    return itemlist

def play(item):
    logger.info()
    itemlist = []

    if "stream/amz.php" in item.url:
        if not item.url.startswith("http"):
            item.url = host + item.url[1:]
        data = httptools.downloadpage(item.url).data
        url_play = scrapertools.find_single_match(data, '"file":"([^"]+)').replace("\\/", "/")
    else:
        url_play = item.url

    #logger.debug(url_play)    

    if url_play:
        itemlist.append(item.clone(url = url_play.replace("\\/", "/")))

    return itemlist

def search(item, texto):
    logger.info()

    try:
        item.url = host + 'animes?q=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

