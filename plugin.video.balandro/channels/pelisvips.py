# -*- coding: utf-8 -*-

import re

from platformcode import logger
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://pelisvips.com/'


IDIOMAS = {'es_es': 'Esp', 'la_la': 'Lat', 'en_es': 'Vose', 'en_en': 'VO', 
           'castellano': 'Esp', 'latino': 'Lat', 'subtitulada': 'Vose', 'es': 'Esp', 'la': 'Lat', 'sub': 'Vose'}


def item_configurar_proxies(item):
    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = 'Configurar proxies a usar ...', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)

def do_downloadpage(url, post=None):
    # ~ data = httptools.downloadpage(url).data
    data = httptools.downloadpage_proxy('pelisvips', url, post=post).data

    return data


def mainlist(item):
    return mainlist_pelis(item)

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title='Catálogo', action='list_all', url=host ))

    itemlist.append(item.clone( title='Estrenos', action='list_all', url=host + 'genero/estrenos/' ))
    itemlist.append(item.clone( title='Netflix', action='list_all', url=host + 'genero/netflix/' ))

    itemlist.append(item.clone( title='Castellano', action='list_all', url=host + 'ver-idioma/castellano/' ))
    itemlist.append(item.clone( title='Latino', action='list_all', url=host + 'ver-idioma/latino/' ))
    itemlist.append(item.clone( title='Subtitulado', action='list_all', url=host + 'ver-idioma/subtitulada/' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    itemlist.append(item_configurar_proxies(item))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title='En nueva calidad', action='list_all', url=host + 'genero/nueva-calidad/' ))
    itemlist.append(item.clone( title='En HD 1080p', action='list_all', url=host + 'ver-calidad/hd1080p/' ))
    itemlist.append(item.clone( title='En HD 720p', action='list_all', url=host + 'ver-calidad/hd720p/' ))
    itemlist.append(item.clone( title='En BR screener', action='list_all', url=host + 'ver-calidad/br-screener/' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Películas por género</div>(.*?)</div>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)"><span class="icon"></span>([^<]+)')
    for url, title in matches:
        if 'genero/estrenos/' in url: continue
        elif 'genero/nueva-calidad/' in url: continue
        elif 'genero/netflix/' in url: continue

        itemlist.append(item.clone( action='list_all', title=title, url=url ))

    return sorted(itemlist, key=lambda it: it.title)


def list_all(item): 
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<div id="movie-list"(.*?)<ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a(.*?)</a>')

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="([^"]+)')
        qlty = scrapertools.find_single_match(match, '<span[^>]*>(.*?)</span>')
        title = scrapertools.find_single_match(match, ' alt="([^"]+)')
        thumb = scrapertools.find_single_match(match, ' src="([^"]+)"')

        year = scrapertools.find_single_match(match, '<div class="label_year">(\d{4})')
        if year:
            title = title.replace('(%s)' % year, '').strip()
        else:
            year = '-'

        # Mejorar detección en tmdb. Ejs: Noche de juegos (Game Night) (2018), Juego Macabro / Juego del miedo (Saw) (2004)
        if ' / ' in title: title_alt = title.split(' / ')[0].strip()
        elif ' (' in title: title_alt = title.split(' (')[0].strip()
        else: title_alt = ''

        langs = scrapertools.find_multiple_matches(match, 'flags/([^.]+)')

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, 
                                    languages=','.join([IDIOMAS.get(lang, lang) for lang in langs]), qualities=qlty,
                                    contentType='movie', contentTitle=title, infoLabels={'year': year}, contentTitleAlt = title_alt ))

    tmdb.set_infoLabels(itemlist)

    next_page = scrapertools.find_single_match(data, '<a class="nextpostslink" rel="next" href="([^"]+)')
    if next_page != '':
        itemlist.append(item.clone( title='>> Página siguiente', action='list_all', url = next_page, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    for lang in ['la', 'es', 'sub']:
        bloque = scrapertools.find_single_match(data, '<ul id="source-list">\s*(<li><a id="op1_%s".*?)</ul>' % lang)
        matches = scrapertools.find_multiple_matches(bloque, '<li(.*?)</li>')
        for match in matches:
            url = scrapertools.find_single_match(match, ' rel="([^"]+)')
            if not url: continue

            url = url.replace('www.pelisup.com/v/', 'www.fembed.com/v/')
            url = url.replace('www.pelispp.com/v/', 'www.fembed.com/v/')
            if host in url:
                servidor = 'directo' # '' indeterminado sería más correcto pero como parecen todos de googleapis ponemos directo
            else:
                servidor = servertools.get_server_from_url(url, disabled_servers=True)
                if servidor:
                    url = servertools.normalize_url(servidor, url)
                else:
                    servidor = scrapertools.find_single_match(match, ' title="([^"]+)')

            if url in [it.url for it in itemlist]: continue # evitar duplicados
            qlty = scrapertools.find_single_match(match, '<span class="q">([^<]+)').strip()

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, 
                                  language = IDIOMAS.get(lang, lang), quality = qlty ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if host in item.url:
        data = do_downloadpage(item.url)
        # ~ logger.debug(data)
        url = scrapertools.find_single_match(data, "sources:.*?'file':\s*'([^']+)")
        if url:
            servidor = servertools.get_server_from_url(url)
            if (servidor and servidor != 'directo') or 'storage.googleapis.com/' in url or 'googleusercontent.com/' in url:
                url = servertools.normalize_url(servidor, url)
                itemlist.append(item.clone( url=url, server=servidor ))

    elif item.server and item.url:
        itemlist.append(item.clone())

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('<li class="itemlist"(.*?)</li>', re.DOTALL).findall(data)

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="([^"]+)')
        title = scrapertools.find_single_match(match, ' title="([^"]+)')
        thumb = scrapertools.find_single_match(match, ' src="([^"]+)"')

        year = scrapertools.find_single_match(title, '\((\d{4})\)$')
        if year:
            title = title.replace('(%s)' % year, '').strip()
        else:
            year = '-'

        qlty = scrapertools.find_single_match(match, 'Calidad:\s*<a[^>]+>([^<]+)')
        plot = scrapertools.find_single_match(match, '<p class="text-list">(.*?)</p>')
        langs = scrapertools.find_multiple_matches(match, '/ver-idioma/([^/]+)')

        # Mejorar detección en tmdb. Ejs: Noche de juegos (Game Night) (2018), Juego Macabro / Juego del miedo (Saw) (2004)
        if ' / ' in title: title_alt = title.split(' / ')[0].strip()
        elif ' (' in title: title_alt = title.split(' (')[0].strip()
        else: title_alt = ''

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, 
                                    languages=','.join([IDIOMAS.get(lang, lang) for lang in langs]), qualities=qlty,
                                    contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot}, contentTitleAlt = title_alt ))

    tmdb.set_infoLabels(itemlist)

    next_page = scrapertools.find_single_match(data, '<a class="nextpostslink" rel="next" href="([^"]+)')
    if next_page != '':
        itemlist.append(item.clone( title='>> Página siguiente', action='list_search', url = next_page, text_color='coral' ))

    return itemlist


def search(item, texto):
    logger.info("texto: %s" % texto)
    try:
        item.url = host + '?s=' + texto.replace(" ", "+")
        return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
