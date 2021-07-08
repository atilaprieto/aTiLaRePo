# -*- coding: utf-8 -*-

import re, base64

from platformcode import logger
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'http://pelisgratis.nu/'

perpage = 18


IDIOMAS = {'latino': 'Lat', 'espanol': 'Esp', 'castellano': 'Esp', 'subtitulado': 'Vose', 'subtitulo': 'Vose'}


def do_downloadpage(url, post=None, headers=None):
    raise_weberror = False if '/ano/' in url else True

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    return data


def mainlist(item):
    return mainlist_pelis(item)

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'genero/estrenos/' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '<h5>Géneros</h5>(.*?)<h5>Películas por Calidad</h5>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        if 'genero/estrenos/' in url: continue

        itemlist.append(item.clone( action='list_all', title=title, url=url ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = host + 'idioma/espanol/' ))
    itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = host + 'idioma/latino/' ))
    itemlist.append(item.clone( title = 'Subtitulado', action = 'list_all', url = host + 'idioma/subtitulada/' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1969, -1):
        itemlist.append(item.clone( title=str(x), url= host + 'ano/' + str(x) + '/', action='list_all' ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '<h5>Películas por Calidad</h5>(.*?)<h5>Películas Más Vistas</h5>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( title = 'En ' + title, url = url, action = 'list_all' ))

    return sorted(itemlist, key = lambda it: it.title)


def list_all(item): 
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)

    patron = '<article class="item.*?href="([^"]+)" title="([^"]+)">(.*?)<img.*?src="([^"]+)"'

    matches = re.compile(patron, re.DOTALL).findall(data)

    num_matches = len(matches)

    for url, title, info, thumb in matches[item.page * perpage:]:
        quality = scrapertools.find_single_match(info, 'class="calidad">([^<]+)</div>')

        info = scrapertools.find_single_match(info, '<div class="audio">(.*?)</div></div>')
        list_langs = re.compile('<div class="([^"]+)"', re.DOTALL).findall(info)

        langs = extraer_idiomas(list_langs)

        thumb = re.sub('p/w\d+', "p/original", thumb)

        year = scrapertools.find_single_match(url, '-(\d{4})')
        if not year:
            year ='-'

        title = title
        _title = re.sub(' \((.*?)\)$', '', title)

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages = ', '.join(langs),
                                    contentType='movie', contentTitle=_title, infoLabels={'year': year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    buscar_next = True
    if num_matches > perpage:
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title='>> Página siguiente', page=item.page + 1, action='list_all', text_color='coral' ))
            buscar_next = False

    if buscar_next:
        next_page = scrapertools.find_single_match(data, '>Página actual.*?<a class="page-link" href="(.*?)"')
        if next_page:
           itemlist.append(item.clone (url = next_page, page = 0, title = '>> Página siguiente', action = 'list_all', text_color='coral'))

    return itemlist


def extraer_idiomas(list_langs):
    logger.info()

    for i, idioma in enumerate(list_langs):
        lang = IDIOMAS.get(idioma, idioma)
        list_langs[i] = lang

    return list_langs


def puntuar_calidad(txt):
    txt = txt.replace(' ', '').replace('-', '').lower()
    orden = ['tsscreener', 'tshq', 'webs', 'brscreener', 'hdtvrip', 'hd+', 'dvdr', 'hdrip', 'bdrip']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    matches = scrapertools.find_multiple_matches(data, 'aria-labelledby="([^"]+)">(.*?)</li>')

    for lang, data in matches:
        if 'trailer' in lang.lower():
            continue

        matches_langs = scrapertools.find_multiple_matches(data, '<a id="enlace".*?data-href="([^"]+)">.*?<img src.*?>([^<])')

        for _url, infor in matches_langs:
            _url += '=='
            _url_links = base64.urlsafe_b64decode(_url).decode('utf-8')

            datos = httptools.downloadpage(_url_links, headers={"referer": item.url}).data

            datos = re.compile('data-embed="([^"]+)"', re.DOTALL).findall(datos)

            for url in datos:
                url += '=='
                url = base64.urlsafe_b64decode(url).decode('utf-8')

                if '/hqq.' in url: url = ''
                elif '/waaw.' in url: url = ''
                elif '/ninjastream.to/' in url: url = ''

                if url:
                    servidor = servertools.get_server_from_url(url)
                    url = servertools.normalize_url(servidor, url)

                    if servidor: 
                        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, 
                                              language = IDIOMAS.get(lang, lang), quality = item.quality, quality_num = puntuar_calidad(item.quality) ))

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
