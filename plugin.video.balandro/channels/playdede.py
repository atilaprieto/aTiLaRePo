# -*- coding: utf-8 -*-

import os, re, base64

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb, jsontools
from lib.balandroresolver import decrypt

host = 'https://playdede.com/'


developer = False
if config.get_setting('developer_mode', default=False):
    config.set_setting('debug', '2')
    developer = True
else:
    config.set_setting('debug', '0')
    developer = False

playdede_user = decrypt("".join(chr(i) for i in list([89, 121, 99, 69, 116, 66, 117, 47, 81, 110, 51, 87, 88, 119, 61, 61])))

playdede_pass = decrypt("".join(chr(i) for i in list([101, 106, 119, 71, 111, 104, 121, 57, 81, 109, 107, 61])))


perpage = 30


def login():
    logger.info()

    data = httptools.downloadpage(host).data

    if 'UserOn' in data: return True

    data = httptools.downloadpage(host + '/login').data

    post = {'user': playdede_user, 'pass': playdede_pass, '_method': 'auth/login'}
    data = httptools.downloadpage(host + 'ajax.php', post=post).data
    jdata = jsontools.load(data)

    if bool(jdata['reload']):
        return True
    else:
        platformtools.dialog_notification(config.__addon_name, '[COLOR red]Login incorrecto[/COLOR]')
        return False


def mainlist(item):
    logger.info()
    itemlist = []

    access = login()
    if not access:
        platformtools.dialog_notification(config.__addon_name, '[COLOR red]Faltan datos Login[/COLOR]')
        return

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series' ))
    itemlist.append(item.clone( title = 'Anime', action = 'mainlist_anime' ))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    access = login()
    if not access:
        platformtools.dialog_notification(config.__addon_name, '[COLOR red]Faltan datos Login[/COLOR]')
        return

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'peliculas/estrenos/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'peliculas/mejor-valoradas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    access = login()
    if not access:
        platformtools.dialog_notification(config.__addon_name, '[COLOR red]Faltan datos Login[/COLOR]')
        return

    filters = '?genre_id=0&language=0&sublanguage=0&quality=2'

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Novedades', action = 'list_all', url = host + 'series/novedades/', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'series/mejor-valoradas/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    return itemlist


def mainlist_anime(item):
    logger.info()
    itemlist = []

    access = login()
    if not access:
        platformtools.dialog_notification(config.__addon_name, '[COLOR red]Faltan datos Login[/COLOR]')
        return

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'animes/', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Novedades', action = 'list_all', url = host + 'animes/novedades/', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'animes/mejor-valoradas/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', group = 'anime', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', group = 'anime', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)
    patron = '<article id="post-\d+" class="item tvshows">.*?<a href="([^"]+)">'
    patron += '<div class="poster"><img src="([^"]+)" style="[^"]+".*?'
    patron += '.*?div class="data"><p>(\d+)<\/p><h3>([^<]+)'
    matches = re.compile(patron).findall(data)

    num_matches = len(matches)

    for url, thumb, year, title in matches[item.page * perpage:]:
        if not url or not title: continue

        if not item.search_type == "all":
            if item.search_type == "movie":
                if '/serie/' in url: continue
            else:
                if '/pelicula/' in url: continue

        if '/pelicula/' in url:
            sufijo = '' if item.search_type != 'all' else 'movie'

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))
        else:
            sufijo = '' if item.search_type != 'all' else 'tvshow'

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, 
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year':year} ))

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
            if '<div class="pagPlaydede">' in data:
                if 'Pagina Anterior' in data:
                    patron = '<div class="pagPlaydede">.*?Pagina Anterior.*?<a href="([^"]+)'
                else:
                    patron = '<div class="pagPlaydede"><a href="([^"]+)'

                next_url = scrapertools.find_single_match(data, patron)
                if next_url:
                    itemlist.append(item.clone( title = '>> Página siguiente', url = next_url, action = 'list_all', page = 0, text_color = 'coral' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if not item.group:
        if item.search_type == 'movie':
            url_generos = host + 'peliculas/'
        else:
            url_generos = host + 'series/'
    else:
        url_generos = host + 'animes/'

    data = httptools.downloadpage(url_generos).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)
    patron = '<li class="cfilter " data-type="genre" data-value="([^"]+)"><img src="[^"]+"><b>([^<]+)'
    matches = re.compile(patron).findall(data)

    url_generos = url_generos  + "?genre="

    for genre_id, title in matches:
        url = url_generos + genre_id + "&year="

        itemlist.append(item.clone( title = title, action = 'list_all', url = url ))

    if item.search_type == 'movie':
        itemlist.append(item.clone( title = 'Aventura', action = 'list_all', url = url_generos + "aventura&year=" ))
        itemlist.append(item.clone( title = 'Documental', action = 'list_all', url = url_generos + "documental&year=" ))
        itemlist.append(item.clone( title = 'Fantasía', action = 'list_all', url = url_generos + "fantasia&year=" ))
        itemlist.append(item.clone( title = 'Historia', action = 'list_all', url = url_generos + "historia&year=" ))

    return sorted(itemlist,key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    tope_year = 1969

    if not item.group:
        if item.search_type == 'movie':
            url_anios = host + 'peliculas/'
        else:
            url_anios = host + 'series/'
    else:
        url_anios = host + 'animes/'

    url_anios = url_anios + '?genre=&year='

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, tope_year, -1):
        itemlist.append(item.clone( title = str(x), url = url_anios + str(x), action = 'list_all' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    # ~ if developer == True: logger.debug(data)

    patron = "<div class='clickSeason(?: clickAc| )' data-season='(\d+)'"

    temporadas = re.compile(patron, re.DOTALL).findall(data)

    for tempo in temporadas:
        title = 'Temporada ' + tempo

        if len(temporadas) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&'), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = int(tempo)
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = int(tempo), page = 0 ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    perpage = 50

    data = httptools.downloadpage(item.url).data
    # ~ if developer == True: logger.debug(data)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    data = scrapertools.find_single_match(data, "<div class='se-c' data-season='%d'(.*?)<\/div><\/div>" % (item.contentSeason))
    patron = '<a href="([^"]+)"><div class="imagen">'
    patron += '<img src="([^"]+)"><\/div>.*?<div class="epst">([^<]+)'
    patron += '<\/div><div class="numerando">([^<]+)'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, thumb, titulo, name in matches[item.page * perpage:]:
        s_e = scrapertools.get_season_and_episode(name)
        season = int(s_e.split("x")[0])
        episode = s_e.split("x")[1]

        title = str(season) + 'x' + str(episode) + ' ' + titulo

        itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail=thumb,
                                    contentType = 'episode', contentSeason = season, contentEpisodeNumber=episode ))

        if len(itemlist) >= perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if len(matches) > ((item.page + 1) * perpage):
        itemlist.append(item.clone( title=">> Página siguiente", action="episodios", page=item.page + 1, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    access = login()
    if not access:
        platformtools.dialog_notification(config.__addon_name, '[COLOR red]Faltan datos Login[/COLOR]')
        return []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)
    # ~ if developer == True: logger.debug(data)

    top_patron = '><div class="playerItem (?:active|)" data-lang="([^"]+)" '
    top_patron += 'data-loadPlayer="(\d+)">.*?<h3>([^<]+)<\/h3><p>(?:Calidad: |)([^<]+)'
    topmatches = re.compile(top_patron, re.DOTALL).findall(data)

    for lang, sid, server, qlty in topmatches:
        if not server or not sid: continue

        lang = lang.capitalize()
        server = servertools.corregir_servidor(server)

        itemlist.append(Item( channel = item.channel, action = 'play', server = server, title = '', url = '', id=sid, language = lang, quality = qlty ))

    patron = '<li><a href="([^"]+)" rel="nofollow noopener" target="_blank"><span> '
    patron += '<img src="[^"]+">([^<]+)<b>([^<]+)<\/b> <\/span><span> '
    patron += '<img src="assets\/image\/languages\/([^_]+)'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, server, qlty, lang in matches:
        if not url or not server: continue

        lang = lang.capitalize()
        server = servertools.corregir_servidor(server)

        itemlist.append(Item( channel = item.channel, action = 'play', server = server, title = '', url = url, language = lang, id='', quality = qlty ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if item.id:
        post = {'_method': 'getPlayer','id': item.id, 'width': 564, 'height': 540}
        data = httptools.downloadpage(host + 'ajax.php', post=post).data
        jdata = jsontools.load(data)['render']
        url_play = scrapertools.find_single_match(jdata, "src='([^']+)'")
    else:
        url_play = item.url

    if url_play:
        itemlist.append(item.clone(url = url_play.replace("\\/", "/")))

    return itemlist


def search(item, texto):
    logger.info()

    try:
        access = login()
        if not access:
           platformtools.dialog_notification('Playdede', '[COLOR red]Faltan datos Login[/COLOR]')
           return []

        item.url = host + 'search/?s=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
