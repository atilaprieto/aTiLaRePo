# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] >= 3:
    PY3 = True
    import urllib.parse as urllib
else:
    PY3 = False
    import urllib


import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://monoschinos2.com'


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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/animes', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host + '/emision', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'list_epis', url = host, search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    url_genre = host + '/animes'

    data = httptools.downloadpage(url_genre).data

    bloque = scrapertools.find_single_match(data, '>Género<(.*?)</div>')

    matches = re.compile('href="(.*?)">(.*?)</a>').findall(bloque)

    for url, title in matches:
        if title == 'Todo': continue

        url = host + url

        itemlist.append(item.clone( title = title, action = 'list_all', url = url ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    url_anio = host + '/animes'

    data = httptools.downloadpage(url_anio).data

    bloque = scrapertools.find_single_match(data, '>Año<(.*?)</div>')

    matches = re.compile('href="(.*?)">(.*?)</a>').findall(bloque)

    for url, title in matches:
        if title == 'Todo': continue

        url = host + url

        itemlist.append(item.clone( title = title, action = 'list_all', url = url ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    url_cat = host + '/animes'

    data = httptools.downloadpage(url_cat).data

    bloque = scrapertools.find_single_match(data, '>Categoría<(.*?)</div>')

    matches = re.compile('href="(.*?)">(.*?)</a>').findall(bloque)

    for url, title in matches:
        if title == 'Todo': continue

        url = host + url

        itemlist.append(item.clone( title = title, action = 'list_all', url = url ))

    return sorted(itemlist,key=lambda x: x.title)


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = '<article.*?href="([^"]+)">.*?src="([^"]+)".*?<h3 class="Title">([^<]+)</h3>.*?"fecha">([^<]+)<.*?</i>([^<]+)'

    matches = re.compile(patron).findall(data)

    for url, thumb, title, year, plot in matches:
        thumb = re.sub("image/imagen/160/224/", "assets/img/serie/imagen/", thumb)

        itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb, 
                                    contentType = 'tvshow', contentSerieName = title, infoLabels={'year':year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '"page-item active">.*?</a>.*?<a class="page-link" href="([^"]+)">')
        if next_page:
            actual_page = scrapertools.find_single_match(item.url, '([^\?]+)?')

            itemlist.append(item.clone( title = '>> Página siguiente', url = actual_page + next_page, action = 'list_all', text_color = 'coral' ))

    return itemlist


def list_epis(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<section class="caps">(.*?)</section>')

    patron = '<article.*?<a href="([^"]+)">.*?src="([^"]+)".*?class="vista2">([^<]+)</span>.*?<span class="episode">.*?</i>([^<]+)</span>.*?<h2 class="Title">([^<]+)</h2>'

    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for url, thumb, type, epis, title in matches:
        itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail=thumb,
                                    contentSerieName=title, contentType = 'episode', contentSeason = 1, contentEpisodeNumber=epis ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    perpage = 50

    data = httptools.downloadpage(item.url).data

    matches = re.compile('<a class="item" href="(.*?)".*?</i>(.*?)<div', re.DOTALL).findall(data)

    tot_epis = len(matches)

    all_epis = False

    if item.page == 0:
        if tot_epis > 100:
            if platformtools.dialog_yesno(config.__addon_name, 'La serie  ' + '[COLOR tan]' + item.contentSerieName + '[/COLOR] tiene [COLOR yellow]' + str(tot_epis) + '[/COLOR] episodios ¿ Desea cargarlos Todos de una sola vez ?'):
                color_infor = config.get_setting('notification_infor_color', default='pink')
                platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Cargando episodios[/B][/COLOR]' % color_infor)
                all_epis = True

    i = 0

    for url, title in matches[item.page * perpage:]:
        i += 1

        title = title.replace('Sub Español', '').strip()

        itemlist.append(item.clone( action='findvideos', url = url, title = title, contentType = 'episode', contentSeason = 1, contentEpisodeNumber=i ))

        if not all_epis:
            if len(itemlist) >= perpage:
                break

    tmdb.set_infoLabels(itemlist)

    if not all_epis:
        if len(matches) > ((item.page + 1) * perpage):
            itemlist.append(item.clone( title=">> Página siguiente", action="episodios", page=item.page + 1, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = host + '/reproductor\?url=([^&]+)'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for url in matches:
        url = urllib.unquote(url)

        if "cl?url=" in url: continue

        if '?url=' in  url:
            url = scrapertools.find_single_match(url, '.*?url=([^&]+)?')

        if url:
            if '/hqq.' in url or '/waaw.' in url: continue

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            if servidor == 'directo': continue

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = 'Vose' ))

    return itemlist


def search(item, texto):
    logger.info()

    try:
        item.url = host + '/search?q=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

