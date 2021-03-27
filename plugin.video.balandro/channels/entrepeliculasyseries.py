# -*- coding: utf-8 -*-

from platformcode import logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://entrepeliculasyseries.com/'

perpage = 21


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series' ))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'ver-peliculas-online/', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone ( title = 'Por año', action = 'anios', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Últimas recientes', action = 'list_all', url = host + 'series-recientes/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'ver-series-online/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    matches = scrapertools.find_multiple_matches(data, '<li><a class="dropdown-item" href="([^"]+)">(.*?)</a>')

    for url, title in matches:
        if '/ver-' in url: continue
        elif '-del-' in url: continue

        itemlist.append(item.clone( action = 'list_all', title = title, url = url ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 2008, -1):
        url = host + 'peliculas-del-' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<div class="publications-content">(.*?)</a>')
    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        title = scrapertools.find_single_match(match, '<h3>(.*?)</h3>').strip()
        if not title:
            title = scrapertools.find_single_match(match, '<h2>(.*?)</h2>').strip()

        thumb = scrapertools.find_single_match(match, 'src="([^"]+)"')

        url = scrapertools.find_single_match(match, 'href="([^"]+)"')

        if not title or not url: continue

        tipo = 'movie' if '/pelicula/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if '/pelicula/' in url:
            if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': '-'} ))

        if '/serie/' in url:
            if item.search_type == 'movie': continue

            itemlist.append(item.clone( action ='temporadas', url = url, title = title, thumbnail = thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': '-'} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    buscar_next = True
    if num_matches > perpage:
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title='>> Página siguiente', page=item.page + 1, action='list_all', text_color='coral' ))
            buscar_next = False

    if buscar_next:
        if "<span aria-current='page' class='current'>" in data:
            if '>Ultima »</a>' in data:
                next_page_link = scrapertools.find_single_match(data, "<span aria-current='page' class='current'>.*?href=(.*?)>")

                if next_page_link != '':
                    next_page_link =  next_page_link.replace('"', '')
                    itemlist.append(item.clone( title = '>> Página siguiente', action = 'list_all', url = next_page_link, text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<h2 class="number-season">.*?Temporada (.*?)</h2>')
    if not matches: matches = scrapertools.find_multiple_matches(data, '<h2 class="number-season">.*?Tempoarada (.*?)</h2>')

    for nro_season in matches:
        title = 'Temporada ' + nro_season

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&'), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = nro_season
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = nro_season, page = 0 ))

    tmdb.set_infoLabels(itemlist)

    return sorted(itemlist, key=lambda it: it.contentSeason)


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    perpage = 50

    data = httptools.downloadpage(item.url).data

    season = scrapertools.find_single_match(data, '<h2 class="number-season">.*?Temporada.*?' + str(item.contentSeason) + '</h2>(.*?)</ul>')
    if not season: season = scrapertools.find_single_match(data, '<h2 class="number-season">.*?Tempoarada.*?' + str(item.contentSeason) + '</h2>(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(season, '<a href="(.*?)">(.*?)<')

    for url, title in matches[item.page * perpage:]:
        title = title.replace(' → ', '')
        nro_epi = scrapertools.find_single_match(url, '-capitulo-(.*?)/')

        titulo = str(item.contentSeason) + 'x' + nro_epi + ' ' + title

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = nro_epi ))

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

    options = scrapertools.find_multiple_matches(data, '<h3 class="select-idioma">(.*?)<div class="col-sm-12 col-md-3 option-lang">')

    for option in options:
        language = scrapertools.find_single_match(option, 'class="text-options" id="(.*?)"').strip()
        language = language.replace('-option', '')

        if language == 'sub': language = 'Vose'
        elif language == 'lat': language = 'Lat'
        elif language == 'esp': language = 'Esp'

        links = scrapertools.find_multiple_matches(option, '<li class="option" data-link="(.*?)".*?</noscript></span>(.*?)</a>')

        for url, servidor in links:
            servidor = servidor.strip()

            if servidor:
               servidor = servidor.lower()

               if servidor == 'google drive': servidor ='gvideo'

               itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = language ))

    # Descargas
    if '> Descargar </button>' in data:
        matches = scrapertools.find_multiple_matches(data, '<div class="row option-down-(.*?)</a></div>')

        patron = '.*?<div class="col-3">(.*?)</div>.*?<div class="col-3">(.*?)</div>.*?<div class="col-3">(.*?)</div>.*?href="(.*?)"'

        for match in matches:
            descargas = scrapertools.find_multiple_matches(match, patron)
            if not descargas:
                patron = '.*?<div class="col-3"(.*?)</div>.*?<div class="col-3">(.*?)</div>.*?<div class="col-3">(.*?)</div>.*?href="(.*?)"'

            for servidor, language, qlty, url in descargas:
                language = language.strip()

                if language == 'Subtitulado': language = 'Vose'
                elif language == 'Latino': language = 'Lat'
                elif language == 'Castellano': language = 'Esp'

                qlty = qlty.replace(' - ', ' ').strip()

                servidor = servidor.strip()

                if servidor:
                    servidor = servidor.lower()
                    if 'descargar por' in servidor:
                        servidor = scrapertools.find_single_match(servidor, '">(.*?)$').strip()
                    elif servidor == '1fitchier': continue

                    if servidor:
                        other = 'D'

                        if servidor == 'google drive': servidor ='gvideo'

                        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = language,
                                              quality = qlty, other = other ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url
    servidor = item.server

    if item.other == 'D':
       if '/go.php?' in url:
           data = httptools.downloadpage(url).data
           url = scrapertools.find_single_match(data, '<a id="DownloadScript" href="([^"]+)"')

           if '//cuon.io/' in url or '/uii.io/' in url: return itemlist

           if url:
               servidor = servertools.get_server_from_url(url)
               servidor = servertools.corregir_servidor(servidor)

    elif url.startswith(host):
       if '/ir.php?' in url:
           data = httptools.downloadpage(url).data

           url = scrapertools.find_single_match(data, 'window.location="([^"]+)"')

           if url:
               servidor = servertools.get_server_from_url(url)
               servidor = servertools.corregir_servidor(servidor)

    if url:
        if not url.startswith('http'): url = 'https:' + url

        itemlist.append(item.clone(server = servidor, url = url))

    return itemlist


def search(item, texto):
    logger.info("texto: %s" % texto)
    try:
        item.url = host + '?s=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

