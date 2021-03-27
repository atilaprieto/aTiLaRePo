# -*- coding: utf-8 -*-

import re

from platformcode import logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools, jsontools


host = 'https://www.cinematteflix.com/'


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host ))

    itemlist.append(item.clone( title = 'Destacadas', action = 'list_all', url = host + 'search/label/CINEMATTE%20FLIX%20DESTACADOS/' ))

    itemlist.append(item.clone( title = 'Colecciones', action = 'colecciones', url = host ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por décadas', action = 'decadas', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    bloque = scrapertools.find_single_match(data, "id='PageList2'>(.*?)</ul>")

    matches = scrapertools.find_multiple_matches(bloque, '<li>(.*?)</li>')

    for match in matches:
        url = scrapertools.find_single_match(match, "<a href='(.*?)'")
        if url == 'http://': continue

        title = scrapertools.find_single_match(match, "<a href=.*?'>(.*?)</a>")
        if title == 'COLECCIONES': continue

        title = title.replace('CINE DE ', '').replace('CINE ', '')

        if title == 'ESPAÑOL': continue
        elif title == 'LOS 80s': continue
        elif 'OBRAS CLAVES' in title: continue
        elif title == 'OBRAS MAESTRAS': continue
        elif 'OTROS IDIOMAS' in title: continue
        elif title == 'RUSO': continue
        elif title == 'CULTO': continue
        elif 'VHS / BETAMAX' in title: continue

        if 'ARTES MARCIALES' in title: title = 'ARTES MARCIALES'
        elif title == 'PELÍCULAS EXPLOITATION': title = 'EXPLOITATION'
        elif 'ROMÁNTICAS' in title: title = 'ROMÁNTICO'
        elif title == 'SUSPENSE/THRILLER': title = 'THRILLER'

        title = title.lower()
        title = title.capitalize()

        title = title.replace('Á', 'á').replace('É', 'é').replace('Í', 'í').replace('Ó', 'ó').replace('Ú', 'ú').replace('Ñ', 'ñ').replace('Ü', 'ú')

        url = url.replace('https://cinematteflix.blogspot.com/', host)

        itemlist.append(item.clone( title = title, url = url, action = 'list_all' ))

    return sorted(itemlist, key = lambda it: it.title)


def colecciones(item):
    logger.info()
    itemlist = []

    seleccion = [ 
	    ['search/label/John%20Ford', 'John Ford'],
        ['2020/09/coleccion-max-steel-varias-peliculas.html', 'Max Steel'],
        ['2020/09/coleccion-john-wayne-varios-westerns-24.html', 'John Wayne'],
        ['search/label/MARVEL%20RETRO', 'Cine Marvel'],
        ['2020/09/coleccion-peliculas-ghibli-19852020.html', 'Ghibli'],
        ['2020/08/coleccion-deathstalker-1983-1991.html', 'Deathstalker'],
        ['2020/08/coleccion-proyecto-terror-1988-98.html', 'Cine Terror'],
        ['search/label/CINEMATTE%20FLIX%20POR%20MUJERES', 'Películas Olvidadas'],
        ['search/label/CINEMATTE%20FLIX%20ESPAÑOL', 'Cine Español'],
        ['search/label/CINEMATTE%20FLIX%2080', 'Años 80s'],
        ['search/label/CINEMATTE%20FLIX%20ACTUAL', 'Obras Claves'],
        ['search/label/CINEMATTE%20FLIX%20OBRA%20MAESTRA', 'Obras Maestras'],
        ['search/label/CINEMATTE%20FLIX%20OTROS%20IDIOMAS', 'Películas Otros Idiomas'],
        ['search/label/CINEMATTE%20FLIX%20RUSO', 'Cine Ruso'],
        ['search/label/CINEMATTE%20FLIX%20CULTO', 'Cine de Culto'],
        ['search/label/CINEMATTE%20FLIX%20VIDEOCLUB', 'VHS / Betamax']
        ]

    for coleccion, title in seleccion:
        url = host + coleccion
        if not '/coleccion' in coleccion:
            itemlist.append(item.clone( title = 'Colección ' + title, action = 'list_all', url = url ))
        else:
            itemlist.append(item.clone( title = 'Colección ' + title, action = 'list_col', url = url, grupo = 'colec' ))

    return sorted(itemlist, key = lambda it: it.title)


def decadas(item):
    logger.info()
    itemlist = []

    seleccion = [ '10s', '20s', '30s', '40s', '50s', '60s', '70s', '80s', '90s', '00s' ]

    for decada in seleccion:
        url = host + 'search/label/' + decada
        itemlist.append(item.clone( title = 'Década años ' + decada, action = 'list_all', url = url))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1915, -1):
        url = host + 'search/label/' + str(x)
        itemlist.append(item.clone( action= 'list_all', title = str(x), url = url ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, "<article class='post-outer-container'>(.*?)</article>")

    i = 0

    for match in matches:
        url = scrapertools.find_single_match(match, "<a href='(.*?)'")
        if not url: continue

        if '/www.passionatte.com/' in url: continue

        thumb = scrapertools.find_single_match(match, '"ImageObject","url": "(.*?)"')
        info = scrapertools.find_single_match(match, "<div class='r-snippetized'>(.*?)</div>")

        year = scrapertools.find_single_match(info, "\d{4}")
        if '/search?' in item.url:
            if not year: continue

        if year.startswith("8") == True: continue

        if not year: year = '-'

        capitulos = False
        if '-serie-' in url: capitulos = True
        elif '-temporada-' in url: capitulos = True
        elif ' temporada' in info.lower(): capitulos = True
        elif ' temporadas' in info.lower(): capitulos = True

        if 'subtitulada' in info.lower() or 'subtitulado' in info.lower(): langs = 'Vose'
        elif 'V.O.S.E.' in info: langs = 'Vose'
        elif 'V.O.' in info: langs = 'Vo'
        elif 'Versión ' in info: langs = 'Vo'
        else: langs = 'Esp'

        title = info.split("|")[0]
        title = re.sub(r" \(.*?\)", "", title)

        if not item.grupo == 'colec':
            if 'COLECCIÓN ' in title: continue

        title = title.lower().strip()

        title = title.capitalize()

        if title.startswith('Videoclub') == True: continue
        elif title.startswith('Crítica') == True: continue
        elif title.startswith('Resumen') == True: continue
        elif title.startswith('Tutorial') == True: continue
        elif title.startswith('Análisis') == True: continue
        elif title.startswith('Anécdotas') == True: continue
        elif title.startswith('Películas') == True: continue
        elif title.startswith('Premios') == True: continue
        elif title.startswith('Estrenos') == True: continue
        elif title.startswith('Mejores') == True: continue
        elif title.startswith('Taquilla') == True: continue
        elif title.startswith('Desnudas') == True: continue
        elif title.startswith('Oscars') == True: continue
        elif title.startswith('Series') == True: continue

        title = title.replace('Á', 'á').replace('É', 'é').replace('Í', 'í').replace('Ó', 'ó').replace('Ú', 'ú').replace('Ñ', 'ñ').replace('Ü', 'ú')

        i += 1

        if capitulos:
            datos_cap = httptools.downloadpage(url).data
            hay_capitulos = scrapertools.find_multiple_matches(datos_cap, '<iframe allow=.*?src="(.*?)"')
            if len(hay_capitulos) <= 1: capitulos = False

        if not capitulos:
            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, languages = langs, grupo = item.grupo,
                                        contentType = 'movie', contentTitle = title, infoLabels={'year': year} ))
        else:
            itemlist.append(item.clone( action = 'list_col', url = url, title = title, thumbnail = thumb, languages = langs, grupo = 'colec',
                                        contentType = 'movie', contentTitle = title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    next_page = scrapertools.find_single_match(data, "<a class='blog-pager-older-link' href='(.*?)'")

    if next_page:
        if i > 0:
             sgte = True
             if '/label/' in item.url:
                  if i <= 15: sgte = False

             if sgte == True:
                 itemlist.append(item.clone( title = '>> Página siguiente', url = next_page, action = 'list_all', text_color='coral' ))

    return itemlist


def list_col(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<iframe allow=.*?src="(.*?)"')

    if matches: platformtools.dialog_notification('CinematteFlix', '[COLOR blue]Cargando vídeos [/COLOR]')

    nro = 1

    for url in matches:
        if not 'youtube' in url: continue

        try:
            info_url = 'https://www.youtube.com/oembed?url=%s&format=json' % url.replace('/embed/', '/watch?v=')

            data = httptools.downloadpage(info_url).data
            info = jsontools.load(data)

            title = info['title'].replace(' HD', '')
            thumb = info["thumbnail_url"]
            titulo = title
        except:
            titulo = ''
            no_title = re.sub(r":|colecciÓn|'|\d+", "", item.title.lower()).strip()
            if nro == 1:
                title = no_title
            else:
                title = no_title + ' ' + str(nro)

            thumb = item.thumbnail
            nro += 1

        year = scrapertools.find_single_match(title, "\d{4}")

        if not year: year = '-'
        else:
            if ' (' + year + ')' in title: title = title.replace(' (' + year + ')', '').strip()
            elif ' ' + year + ')' in title: title = title.replace(' ' + year + ')', ')').strip()
            elif year in title: title = title.replace(year, '').strip()

        if 'subtitulada' in title.lower() or 'subtitulado' in title.lower(): langs = 'Vose'
        elif 'V.O.S.E.' in title: langs = 'Vose'
        elif 'V.O.' in title: langs = 'Vo'
        elif 'Versión ' in title: langs = 'Vo'
        else: langs = 'Esp'

        title = title.lower().strip()

        title = title.capitalize()

        title = title.replace('Á', 'á').replace('É', 'é').replace('Í', 'í').replace('Ó', 'ó').replace('Ú', 'ú').replace('Ñ', 'ñ').replace('Ü', 'ú')

        title = title.replace('peliculas completas', '').replace('pelicula completa', '').replace('pelicula', '').replace('film completo', '')
        title = title.replace('en español', '').replace('español', '').replace('castellano', '').replace('subtitulada', '').replace('subtitulado', '')

        title = title.strip()

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, languages = langs, grupo = item.grupo,
                                    contentType = 'movie', contentTitle = titulo, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    if item.grupo == 'colec':
        url = item.url
    else:
        data = httptools.downloadpage(item.url).data
        url = scrapertools.find_single_match(data, '<iframe.*?src="(.*?)"')

    if url:
        servidor = servertools.get_server_from_url(url)

        if servidor and servidor != 'directo':
            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, title = '', language = item.languages)) 

    return itemlist


def search(item, texto):
    logger.info("texto: %s" % texto)
    try:
        item.url = host + 'search?q=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
