# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools


host = "https://seriesanimadas.org/"


def mainlist(item):
    return mainlist_anime(item)


def mainlist_anime(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    if descartar_xxx: return itemlist
    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False:
            return itemlist

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'list_epis', url = host, search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host + 'emision', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'series/estrenos', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más populares', action = 'list_all', url = host + 'series/populares', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos',  search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    url_genre = host + '/tvgenero/'

    data = httptools.downloadpage(host + 'series').data

    matches = scrapertools.find_multiple_matches(data, '/tvgenero/(.*?)".*?>(.*?)</a>')

    for genre, title in matches:
        url = url_genre + genre

        itemlist.append(item.clone( title = title, action = 'list_all', url = url ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="(.*?)"')
        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')
        title = scrapertools.find_single_match(match, ' title="(.*?)"')

        if not url or not title: continue

        itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, contentType = 'tvshow', contentSerieName = title ))

    if itemlist:
        next_page = scrapertools.find_single_match(data,'<ul class="pagination">.*?Previous.*?href="(.*?)"')
        if next_page:
            itemlist.append(item.clone( title = '>> Página siguiente', action = 'list_all', url = next_page, text_color = 'coral' ))

    return itemlist


def list_epis(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = '<div class="card-episodie shadow-sm">.*?<a href="(.*?)".*?title="(.*?)".*?src="(.*?)".*?</div>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, title, thumb in matches:
        c_title, epis, lang = scrapertools.find_single_match(title, r'^(.*?)\s*(?:Episodio)?\s*(\d+)\s*(.*)')

        if c_title == 'ver': c_title = title

        c_title = c_title.replace('ver ', '').strip()

        titulo = '1x%s %s' % (epis, c_title)

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail = thumb,
									contentSerieName = title, contentType = 'episode', contentSeason = 1, contentEpisodeNumber = epis ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    matches = re.compile('<div id="season-(.*?)"', re.DOTALL).findall(data)

    if not matches:
        itemlist = episodios(item)
        return itemlist

    for season in matches:
        title = 'Temporada ' + season

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + item.title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = season
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = season, page = 0 ))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    perpage = 50

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    if not item.contentSeason:
        item.contentSeason = 1
        patron = '<a class="episodie-list" href="([^"]+)" .*?</i> Episodio (\d+).*?</span>'
    else:
        patron = 'class="episodie-list" href="([^"]+)" title=".*?Temporada %s .*?pisodio (\d+).*?">' % str(item.contentSeason)

    matches = re.compile(patron, re.DOTALL).findall(data)

    if not matches:
        patron = 'class="episodie-list" href="([^"]+)" title=".*?pisodio (\d+).*?">'
        matches = re.compile(patron, re.DOTALL).findall(data)

    tot_epis = len(matches)

    all_epis = False

    if item.page == 0:
        if tot_epis > 100:
            if platformtools.dialog_yesno(config.__addon_name, 'La serie  ' + '[COLOR tan]' + item.contentSerieName + '[/COLOR] tiene [COLOR yellow]' + str(tot_epis) + '[/COLOR] episodios ¿ Desea cargarlos Todos de una sola vez ?'):
                color_infor = config.get_setting('notification_infor_color', default='pink')
                platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Cargando episodios[/B][/COLOR]' % color_infor)
                all_epis = True

    for url, epis in matches[item.page * perpage:]:
        titulo = '%sx%s - Episodio %s' % (item.contentSeason, epis, epis)

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, 
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

        if not all_epis:
            if len(itemlist) >= perpage:
                break

    if not all_epis:
        if tot_epis > ((item.page + 1) * perpage):
            itemlist.append(item.clone( title=">> Página siguiente", action="episodios", page=item.page + 1, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'latino': 'Lat', 'audio latino': 'Lat', 'español': 'Esp', 'audio español': 'Esp', 'sub español': 'Vose', 'subtitulado': 'Vose'}

    data = httptools.downloadpage(item.url).data

    patron = 'video\[(\d+)\] = .*?src="([^"]+)".*?;'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for option, url in matches:
        lang = scrapertools.find_single_match(data, '"#option%s".*?<span>(.*?)</span>' % str(option))
        lang = lang.strip().lower()

        if 'redirect' in url:
            url_data = httptools.downloadpage(url).data
            url = scrapertools.find_single_match(url_data,'var redir = "([^"]+)";')
            if not url:
                url = scrapertools.find_single_match(url_data,'window.location.href = "([^"]+)";')

        if '/hqq.' in url or '/waaw.' in url: url = ''
        elif '/badshare.io/' in url: url = ''

        if url:
            if url.startswith('//'): url = 'https:' + url

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            if servidor == 'directo': continue

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = IDIOMAS.get(lang, lang) ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url =  host + "search?s=" + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
