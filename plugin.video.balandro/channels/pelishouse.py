# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] < 3:
    import urlparse
else:
    import urllib.parse as urlparse

import os, re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb, jsontools

host = 'https://pelishouse.com/'


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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'movies/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'genre/mas-vistas/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_top', url = host + 'pelislatino24-tv/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Marvel', action = 'list_all', url = host + 'genre/marvel/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'En 3D', action = 'list_3d', url = host + 'quality/3d/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por país', action = 'paises', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo series Tv', action = 'list_all', url = host + 'tvshows/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Catálogo series Animadas', action = 'list_all', url = host + 'genre/series-animadas-gratis/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_top', url = host + 'pelislatino24-tv/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie':
       itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = host + 'genre/castellano/' ))
       itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = host + 'genre/latino/' ))
       itemlist.append(item.clone( title = 'En inglés', action = 'list_all', url = host + 'genre/peliculas-en-ingles/' ))
       itemlist.append(item.clone( title = 'Subtitulado', action = 'list_all', url = host + 'genre/peliculas-subtituladas/' ))
    else:
       itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = host + 'genre/series-en-espanol-castellano/' ))
       itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = host + 'genre/series-en-espanol-latino/' ))
       itemlist.append(item.clone( title = 'Subtitulado', action = 'list_all', url = host + 'genre/series-subtituladas/' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    data = httptools.downloadpage(host).data

    bloque = scrapertools.find_single_match(data, 'Generos</a>(.*?)>MARVEL</a>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        if title == '+18': continue
        elif title == 'Castellano': continue
        elif title == 'Latino': continue
        elif title == 'MARVEL': continue
        elif title == 'Mas Vistas': continue
        elif title == 'Próximamente': continue

        elif 'Peliculas ' in title: continue
        elif 'Series ' in title: continue

        if title == 'CINECALIDAD':
            title = 'CineCalidad'
        elif title == 'descargacineclasico.tv':
           title = 'DescargaCineClasico'

        if item.search_type == 'tvshow':
           if '/accion/' in url: continue
           elif '/aventura/' in url: continue
           elif '/belica/' in url: continue
           elif '/ciencia-ficcion/' in url: continue
           elif '/fantasia/' in url: continue
           elif '/musica/' in url: continue
           elif '/romance/' in url: continue
           elif '/suspense/' in url: continue
        else:
           if '/reality/' in url: continue
           elif '/sci-fi-fantasy/' in url: continue
           elif '/war-politics/' in url: continue

        itemlist.append(item.clone( title = title, url = url, action = 'list_all' ))

    if item.search_type == 'movie':
        itemlist.append(item.clone( action = 'list_all', title = 'CineCalidad Top', url = host + 'genre/cinecalidad-top/' ))
        itemlist.append(item.clone( action = 'list_all', title = 'Películas de Televisión', url = host + 'genre/pelicula-de-la-television/' ))
        itemlist.append(item.clone( action = 'list_all', title = 'Películas de Tv', url = host + 'genre/pelicula-de-tv/' ))

        if not descartar_xxx:
            itemlist.append(item.clone( action = 'list_all', title = 'xxx / adultos', url = host + 'search?s=adultos' ))

    return sorted(itemlist, key=lambda it: it.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1938, -1):
        itemlist.append(item.clone( title = str(x), url = host + 'release/' + str(x) + '/', action = 'list_all' ))

    return itemlist


def paises(item):
    logger.info()
    itemlist = []

    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    data = scrapertools.find_single_match(data, '<ul class="genres scrolling">(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(data, '<a href="([^"]+)" title="[^"]+">([^<]+)</a>')

    for url, title in matches:
        if not 'Peliculas ' in title: continue

        if 'En Ingles' in title: continue
        elif 'subtituladas' in title: continue

        title = title.replace('Peliculas', '').strip()

        itemlist.append(item.clone( title = title, url = url, action = 'list_all' ))

    itemlist.append(item.clone( action = 'list_all', title = 'Australianas', url = host + 'genre/peliculas-australianas/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Bolivianas', url = host + 'genre/peliculas-bolivianas/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Brasileñas', url = host + 'genre/peliculas-brasilenas/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Canadienses', url = host + 'genre/peliculas-canadienses/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Chinas', url = host + 'genre/peliculas-china/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Colombianas', url = host + 'genre/peliculas-colombianas/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Coreanas', url = host + 'genre/peliculas-coreanas/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Españolas', url = host + 'genre/peliculas-espanolas/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Estadounidenses', url = host + 'genre/peliculas-estadounidenses/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Francesas', url = host + 'genre/peliculas-francesas/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Indias', url = host + 'genre/peliculas-indias/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Italianas', url = host + 'genre/peliculas-italianas/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Japonesas', url = host + 'genre/peliculas-japonesas/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Noruegas', url = host + 'genre/peliculas-noruegas/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Panameñas', url = host + 'genre/peliculas-panamenas/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Peruanas', url = host + 'genre/peliculas-peruanas/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Tailandesas', url = host + 'genre/peliculas-tailandesa/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Taiwanesas', url = host + 'genre/peliculas-taiwanesas/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Uruguayas', url = host + 'genre/peliculas-uruguayas/' ))

    itemlist.append(item.clone( action = 'list_all', title = 'Checas', url = host + 'genre/peliculas-de-chequia/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Guatemaltecas', url = host + 'genre/peliculas-de-guatemala/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Islandesas', url = host + 'genre/peliculas-de-islandia/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Inglesas', url = host + 'genre/peliculas-de-reino-unido/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Rusas', url = host + 'genre/peliculas-de-rusia/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Sudafricanas', url = host + 'genre/peliculas-de-sudafrica/' ))

    return sorted(itemlist, key=lambda it: it.title)


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    data = scrapertools.find_single_match(str(data), '<h2>Añadido(.*?)alt="PELISHOUSE"')
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    if item.search_type == 'movie':
        for match in matches:
            url = scrapertools.find_single_match(match, '<a href="(.*?)"')
            if 'tvshows' in url: continue

            thumb = scrapertools.find_single_match(match, 'src="(.*?)"')
            title = scrapertools.find_single_match(match, 'alt="(.*?)"')
            qlty = scrapertools.find_single_match(match, 'class="quality">(.*?)</span>')
            year = scrapertools.find_single_match(match, '</h3>.*?<span>(\d+)</span>')

            title = title.strip()

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    else:
        for match in matches:
            url = scrapertools.find_single_match(match, '<a href="(.*?)"')
            if 'movies' in url: continue

            thumb = scrapertools.find_single_match(match, 'src="(.*?)"')
            title = scrapertools.find_single_match(match, 'alt="(.*?)"')
            year = scrapertools.find_single_match(match, '</h3>.*?<span>(\d+)</span>')

            title = scrapertools.find_single_match(title, '(.*?) Serie.*?nline') or title

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    next_page = ''
    if item.search_type == 'movie':
        next_page = scrapertools.find_single_match(data, '<a class=\'arrow_pag\' href="([^"]+)">')
        if not next_page:
            next_page = scrapertools.find_single_match(data, '<span class="current">\d+</span><a href=\'([^\']+)\' class="inactive">')
    else:
        next_page = scrapertools.find_single_match(data, '<span class="current">\d+</span><a href=\'([^\']+)\' class="inactive">')

    if next_page:
        itemlist.append(item.clone(title = '>> Página siguiente', url = next_page, action = 'list_all', text_color = 'coral'))

    return itemlist


def list_top(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')
        title = scrapertools.find_single_match(match, 'alt="(.*?)"')
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        qlty = scrapertools.find_single_match(match, 'class="quality">(.*?)</span>')
        year = scrapertools.find_single_match(match, '</h3>.*?<span>(\d+)</span>')

        year = scrapertools.find_single_match(year, '.*?,(.*?)$').strip()
        if not year: year = '-'

        if item.search_type == 'movie':
            if '/tvshows/' in url: continue

            title = title.strip()

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        else:
            if '/movies/' in url: continue

            title = scrapertools.find_single_match(title, '(.*?) Serie.*?nline') or title

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    next_page = ''
    if item.search_type == 'movie':
        next_page = scrapertools.find_single_match(data, '<a class=\'arrow_pag\' href="([^"]+)">')
        if not next_page:
            next_page = scrapertools.find_single_match(data, '<span class="current">\d+</span><a href=\'([^\']+)\' class="inactive">')
    else:
        next_page = scrapertools.find_single_match(data, '<span class="current">\d+</span><a href=\'([^\']+)\' class="inactive">')

    if next_page:
        itemlist.append(item.clone(title = '>> Página siguiente', url = next_page, action = 'list_top', text_color = 'coral'))

    return itemlist


def list_3d(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')
        title = scrapertools.find_single_match(match, 'alt="(.*?)"')
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        year = scrapertools.find_single_match(match, '</h3>.*?<span>(\d+)</span>')

        title = title.strip()

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                    contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, "<span class='se-t[^']*'>(\d+)</span><span class='title'>([^<]+)")

    for numtempo, title in matches:
        title = title.strip()

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&'), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = numtempo, page = 0 ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    perpage = 50

    data = httptools.downloadpage(item.url).data

    patron = '<li class=\'mark-\d+\'>.*?src=\'([^\']+)\'.*?class=\'numerando\'>(\d+) - (\d+).*?href=\'([^\']+)\'>([^<]+)'

    matches = scrapertools.find_multiple_matches(data, patron)

    for thumb, season, episode, url, title in matches[item.page * perpage:]:
        if item.contentSeason:
            if not str(season) == str(item.contentSeason):
               continue

        titulo = str(item.contentSeason) + 'x' + str(episode) + ' ' + title

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail=thumb,
                                    contentType = 'episode', contentEpisodeNumber = episode ))

        if len(itemlist) >= perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if len(itemlist) > (item.page + 1) * perpage:
        itemlist.append(item.clone( title = ">> Página siguiente", action = "episodios", page = item.page + 1, text_color= 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = "<li id='player-option-\d+' class='dooplay_player_option' data-type='([^']+)'.*?data-post='([^']+)' data-nume='([^'])+'>.*?<span class='title'>([^<]+)</span>"

    matches = scrapertools.find_multiple_matches(data, patron)

    for _type, post, nume, tag in matches:
        url = get_video_url(_type, post, nume)

        try:
           lang, qlty = tag.strip().split(' ')
        except Exception:
           logger.error('idioma-calidad Desconocidos')
           lang = ''
           qlty = ''

        language = detectar_idiomas(lang)

        url = urlparse.urljoin(item.url, url)

        if '/hqq.' in url or '/waaw.' in url or '/www.jplayer.' in url: continue

        if url:
            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            itemlist.append(Item( channel = item.channel, action = 'play', title = '', server = servidor, url = url,
                                  language = language, quality = qlty ))

    patron = "<tr id=.*?src='.*?domain=([^']+)'.*?href='(.*?)'.*?class='quality'>(.*?)</strong></td><td>(.*?)</td><td>"

    matches = scrapertools.find_multiple_matches(data, patron)

    for server, url, qlty, lang in matches:
        language = detectar_idiomas(lang)

        url = urlparse.urljoin(item.url, url)

        if '/hqq.' in url or '/waaw.' in url or '/www.jplayer.' in url: continue

        if url:
            servidor = server.split('.')[0]
            servidor = servertools.corregir_servidor(servidor)

            itemlist.append(Item( channel = item.channel, action = 'play', title = '', server = servidor, url = url, other = 'd',
                                  language = language, quality = qlty ))

    return itemlist


def get_video_url(_type, post, nume):
    data = httptools.downloadpage(host + 'wp-json/dooplayer/v2/%s/%s/%s' % (post, _type, nume)).data

    data = jsontools.load(data)['embed_url']
    return data


def play(item):
    logger.info()
    itemlist = []

    if item.url.startswith(host):
        if item.other == 'd':
            data = httptools.downloadpage(item.url).data
            url = scrapertools.find_single_match(str(data), 'href="(.*?)"')

            if url:
                servidor = servertools.get_server_from_url(url)
                servidor = servertools.corregir_servidor(servidor)
                itemlist.append(item.clone( url=url, server=servidor))

        else:
            data = httptools.downloadpage(item.url).data
            url = scrapertools.find_single_match(str(data), '"file":"(.*?)"')

            if url:
               url = url.replace('\\/', '/')
               itemlist.append(item.clone( url=url, server='directo'))

    elif item.url.startswith('https://peliscalidad.top/'):
        video_id = item.url.split('/')[-1]
        data = httptools.downloadpage('https://peliscalidad.top/api/source/%s' % video_id, post={'r': '', 'd': 'peliscalidad.top'}).data
        data = jsontools.load(data)

        if 'Video not found or has been removed' in str(data):
            return 'Video eliminado'

        for video in data['data']:
            url = httptools.downloadpage(video['file'], follow_redirects=False).headers['location']

            itemlist.append(item.clone( url=url, server='directo'))

    elif item.url.startswith('https://api.cuevana3.io'):
        fid = scrapertools.find_single_match(item.url, "h=([^&]+)")

        if '/fembed/?h=' in item.url:
            api_url = 'https://api.cuevana3.io/fembed/rd.php'
            api_post = 'h=' + fid + '&ver=si'
        elif '/sc/index.php?h=' in item.url:
            api_url = 'https://api.cuevana3.io/sc/r.php'
            api_post = 'h=' + fid
        elif '/ir/goto_ddh.php?h=' in item.url:
            api_url = 'https://api.cuevana3.io/ir/redirect_ddh.php'
            api_post = 'url=' + fid
        else:
            api_url = 'https://api.cuevana3.io/ir/rd.php'
            api_post = 'url=' + fid

        try:
           url = httptools.downloadpage(api_url, post=api_post, follow_redirects=False).headers['location']
        except:
           url = ''

        if url:
            if '/damedamehoy.xyz/' in url:
                url = url.replace('https://damedamehoy.xyz/embed.html#', 'https://damedamehoy.xyz/details.php?v=')
                data = httptools.downloadpage(url).data

                url = scrapertools.find_single_match(data, '"file":"(.*?)"')
                url = url.replace('\\/', '/')

        if url:
            itemlist.append(item.clone( url=url, server='directo'))

    elif item.url.startswith('https://g-nula.top'):
        video_id = item.url.split('/')[-1]
        data = httptools.downloadpage('https://g-nula.top/api/source/%s' % video_id, post={'r': '', 'd': 'g-nula.top'}).data
        data = jsontools.load(data)

        for video in data['data']:
            url = httptools.downloadpage(video['file'], follow_redirects=False).headers['location']

            itemlist.append(item.clone( url=url, server='directo'))

    else:
        itemlist.append(item.clone( url=item.url, server=item.server))

    return itemlist


def detectar_idiomas(tags):
    languages = []

    tags = tags.lower()
    idio = scrapertools.find_multiple_matches(tags, 'rel="tag">(.*?)</a>')

    if idio:
       for idioma in idio:
           if idioma == 'castellano': languages.append('Esp')
           if idioma == 'espaÑol': languages.append('Esp')
           if idioma == 'latino': languages.append('Lat')
           if idioma == 'ingles': languages.append('Eng')
           if idioma == 'subtitulado': languages.append('Vose')
    else:
       if tags == 'castellano': return 'Esp'
       elif tags == 'espaÑol': return 'Esp'
       elif tags == 'latino': return 'Lat'
       elif tags == 'ingles': return 'Eng'
       elif tags == 'subtitulado': return 'Vose'

       elif 'ingles' in tags: return 'Eng'
       elif 'subtitulado' in tags: return 'Vose'
       else:
            return '?'

    return languages


def list_search(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    data = httptools.downloadpage(item.url).data

    if item.search_type == 'movie' or item.search_type == 'all':
        patron = '<a href="([^"]+)"><img src="([^"]+)" alt="([^"]+)" /><span class="movies">Película</span>.*?<span class="year">(\d+)</span>'

        matches = scrapertools.find_multiple_matches(data, patron)

        for url, thumb, title, year in scrapertools.find_multiple_matches(data, patron):
            if descartar_xxx:
                if '/genre/18/' in url: continue

            tipo = 'movie' if '/movies/' in url else 'tvshow'
            sufijo = '' if item.search_type != 'all' else tipo

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo = sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    if item.search_type == 'tvshow' or item.search_type == 'all':
        patron = '<a href="([^"]+)"><img src="([^"]+)" alt="([^"]+)" /><span class="tvshows">TV</span>.*?<span class="year">(\d+)</span>'

        matches = scrapertools.find_multiple_matches(data, patron)

        for url, thumb, title, year in matches:
            title = scrapertools.find_single_match(title, '(?:Ver )?(.*?),? Serie.*?nline') or title

            tipo = 'tvshow' if '/tvshows/' in url else 'movie'
            sufijo = '' if item.search_type != 'all' else tipo

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo = sufijo,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.url = host + '?s=' + texto.replace(" ", "+")
       return list_search(item)
    except:
       import sys
       for line in sys.exc_info():
           logger.error("%s" % line)
       return []
