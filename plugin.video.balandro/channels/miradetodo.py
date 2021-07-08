# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = "https://miradetodo.co/"


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    if '/fecha-estreno/' in url or '/series-lanzamiento/' in url: raise_weberror = False

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    return data


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

    itemlist.append(item.clone( title='Catálogo', action = 'list_all', url = host + 'page/1/?s', search_type = 'movie' ))

    itemlist.append(item.clone( title='Estrenos', action = 'list_all', url = host + 'category/estrenos/page/1/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title='Catálogo', action = 'list_all', url = host + 'series/page/1/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    if item.search_type == 'movie':
        patron = 'id="moviehome".*?<h3>Géneros(.*?)<h3>Año de estreno'
    else:
        patron = 'id="serieshome".*?<h3>Géneros(.*?)<h3>Año de estreno'

    bloque = scrapertools.find_single_match(data, patron)

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?>(.*?)</a>')

    for url, title in matches:
        if '/estrenos/' in url: continue

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, genre = title ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    if item.search_type == 'movie':
        topyear = 1938
        url_any = host + 'fecha-estreno/'
    else:
        topyear = 2002
        url_any = host + 'series-lanzamiento/'

    for x in range(current_year, topyear, -1):
        itemlist.append(item.clone( title=str(x), url = url_any + str(x) + '/', action='list_all' ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '<h3>Calidad(.*?)<B>MiraDeTodo</B')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( title = 'En ' + title, url = url, action = 'list_all' ))

    return sorted(itemlist, key = lambda it: it.title)


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', '', data)

    patron = 'class=item>.*?<a href=(.*?)><div class=image>.*?<img src=(.*?) alt=(.*?) \(\d{4}.*?ttx>(.*?)'
    patron += '<div class=degradado>.*?fixyear><h2>.*?<\/h2>.*?<span class=year>(.*?)<\/span><\/div>(.*?)<\/div>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, thumb, title, plot, year, qlty in matches:

        if qlty:
            qlty = scrapertools.find_single_match(qlty, 'calidad2>(.*?)<')

        if not year:
            year = '-'

        tipo = 'tvshow' if 'series' in item.url or 'series' in url else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'tvshow':
            itemlist.append(item.clone( action='temporadas', url = url, title = title, thumbnail = thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title,  infoLabels = {'year': year, 'plot': plot} ))

        if tipo == 'movie':
            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail=thumb, qualities=qlty, fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, 'alignleft><a href=(.*?) ><\/a><\/div><div class=nav-next alignright>')
        if next_page:
            itemlist.append(item.clone( title = '>> Página siguiente', action='list_all', url = next_page, text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', '', data)

    matches = re.compile('<span class=title>.*?- Temporada (.*?)<\/span>', re.DOTALL).findall(data)

    for season in matches:
        title = 'Temporada ' + season

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = season
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = season, page = 0 ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    perpage = 50

    data = do_downloadpage(item.url)

    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', '', data)

    season = item.contentSeason

    patron = '<li><div class=numerando>%s.*?x.*?(\d+)<\/div>.*?<a href=(.*?)> (.*?)<\/a>.*?<\/i>' % str(season)

    matches = re.compile(patron, re.DOTALL).findall(data)

    for epis, url, title in matches[item.page * perpage:]:
        titulo = season + 'x%s %s' % (epis, title)

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, 
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

        if len(itemlist) >= perpage:
            break

    if len(matches) > ((item.page + 1) * perpage):
        itemlist.append(item.clone( title = ">> Página siguiente", action = "episodios", page = item.page + 1, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'es': 'Esp', 'lat': 'Lat', 'sub': 'Vose', 'Latino': 'Lat', 'Castellano': 'Esp', 'Subtitulado': 'Vose'}

    data = do_downloadpage(item.url)

    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', '', data)

    _data = data

    matches = re.compile('id=(?:div|player)(\d+)>.*?data-lazy-src=(.*?) scrolling', re.DOTALL).findall(data)

    for option, _video in matches:
        sub = ''

        lang = scrapertools.find_single_match(_data, '<a href=#(?:div|player)%s.*?>.*?(.*?)<\/a>' % option)
        if 'audio ' in lang.lower():
            lang = lang.lower().replace('audio ', '')
            lang = lang.capitalize()

        _data_opt = do_downloadpage(_video)

        videos = scrapertools.find_multiple_matches(_data_opt, '<li><a href=(.*?)><span')

        for video in videos:
            _data_video = do_downloadpage(video)

            if 'openload' in video or 'your' in video:
                _url = scrapertools.find_single_match(_data_video, '<li><a href=(.*?srt)><span')
                datos = do_downloadpage(_url)
            else:
                datos = _data_video

            url = scrapertools.find_single_match(datos, 'iframe src=(.*?) scrolling')
            if not url:
                url = scrapertools.find_single_match(datos, "'file':'(.*?)'")

            if url:
                quality = item.qualities

                servidor = servertools.get_server_from_url(url)
                url = servertools.normalize_url(servidor, url)

                itemlist.append(Item(channel = item.channel, action = 'play', server = servidor, title = '', url = url, quality = quality, 
                                     language = IDIOMAS.get(lang,lang) ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.url = host + '?s=' + texto.replace(" ", "+")
       return list_all(item)
    except:
       import sys
       for line in sys.exc_info():
           logger.error("%s" % line)
       return []

