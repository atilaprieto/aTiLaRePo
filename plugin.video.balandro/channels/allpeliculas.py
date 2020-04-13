# -*- coding: utf-8 -*-

import re, base64

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools

HOST = 'https://allpeliculas.tv/'

perpage = 30 # preferiblemente un múltiplo de los elementos que salen en la web (6x10=60) para que la subpaginación interna no se descompense


def mainlist(item):
    return mainlist_pelis(item)

def mainlist_pelis(item):
    logger.info()
    itemlist = []
    
    itemlist.append(item.clone( title='Últimas actualizadas', action='list_all', url=HOST ))
    itemlist.append(item.clone( title='Estrenos', action='list_all', url=HOST + 'genero/estrenos/' ))

    itemlist.append(item.clone( title='Castellano', action='list_all', url=HOST + 'pelicula/tag/espanol/' ))
    itemlist.append(item.clone( title='Latino', action='list_all', url=HOST + 'pelicula/tag/latino/' ))
    itemlist.append(item.clone( title='Subtitulado', action='list_all', url=HOST + 'pelicula/tag/subtitulado/' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone ( title = 'Por año', action = 'anios', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(HOST).data

    bloque = scrapertools.find_single_match(data, 'Categorías</h3> <ul>(.*?)</ul>')
    
    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)">([^<]+)')
    for url, title in matches:
        if 'genero/estrenos/' in url: continue
        itemlist.append(item.clone( action='list_all', title=title, url=url ))

    return sorted(itemlist, key=lambda it: it.title)

def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1953, -1):
        itemlist.append(item.clone( title=str(x), url= HOST + 'pelicula/year_relase/' + str(x) + '/', action='list_all' ))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    matches = re.compile('<div class="col-mt-5 postsh">\s*<div class="poster-media-card">\s*<a(.*?)</a>', re.DOTALL).findall(data)
    num_matches = len(matches)

    for article in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(article, ' href="([^"]+)')
        title = scrapertools.find_single_match(article, ' title="([^"]+)')
        if not url or not title: continue
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        year = scrapertools.find_single_match(article, '<span class="_2Spas">(\d+)</span>')
        if year:
            title = title.replace('(%s)' % year, '').strip()
        else:
            year = '-'

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, 
                                    contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    # Subpaginación interna y/o paginación de la web
    buscar_next = True
    if num_matches > perpage: # subpaginación interna dentro de la página si hay demasiados items
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title='>> Página siguiente', page=item.page + 1, action='list_all' ))
            buscar_next = False

    if buscar_next:
        next_page = scrapertools.find_single_match(data, '<a href="([^"]+)"><i class="glyphicon glyphicon-chevron-right')
        if next_page:
           itemlist.append(item.clone (url = next_page, page = 0, title = '>> Página siguiente', action = 'list_all'))

    return itemlist



# Asignar un numérico según las calidades del canal, para poder ordenar por este valor
def puntuar_calidad(txt):
    txt = txt.replace(' ', '').replace('-', '').lower()
    orden = ['cam', 'ts', 'dvd', 'dvd+', 'hd', 'hd+']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1

def findvideos(item):
    logger.info()
    itemlist = []
    
    IDIOMAS = {'Español': 'Esp', 'Latino': 'Lat', 'Subtitulado': 'VOSE'}

    data = httptools.downloadpage(item.url).data
    # ~ logger.debug(data)

    # Enlaces en embeds
    patron = '<a href="#embed\d+" data-src="([^"]+)" class="([^"]+)"(.*?)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for urlcod, lang, resto in matches:
        cod = urlcod.replace('https://allpeliculas.tv/replayer/', '').split('RRRRR')[0]
        # ~ logger.info('%s %s' % (cod, urlcod))
        numpad = len(cod) % 4
        if numpad > 0: cod += 'R' * (4 - numpad)
        try:
            url = base64.b64decode(cod)
            if numpad > 0: url = url[:-(4 - numpad)]
        except:
            url = None
        if not url: 
            logger.info('No detectada url. %s %s' % (cod, urlcod))
            continue
        
        servidor = servertools.get_server_from_url(url)
        if not servidor or (servidor == 'directo' and 'storage.googleapis.com/' not in url): 
            logger.info('No detectado servidor, url: %s' % url)
            continue
        url = servertools.normalize_url(servidor, url)

        qlty = scrapertools.find_single_match(resto, '([^>]+)</div>$')

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor,
                              title = '', url = url, 
                              language = IDIOMAS.get(lang, lang), quality = qlty, quality_num = puntuar_calidad(qlty), other='e'
                       ))

    # Enlaces en descargas
    bloque = scrapertools.find_single_match(data, 'id="dlnmt"(.*?)</table>')
    matches = re.compile('<tr>(.*?)</tr>', re.DOTALL).findall(bloque)
    for lin in matches:
        if '<th' in lin: continue
        tds = scrapertools.find_multiple_matches(lin, '<td[^>]*>(.*?)</td>')
        url = scrapertools.find_single_match(tds[0], ' href="([^"]+)')
        servidor = scrapertools.find_single_match(tds[1], '<span>(.*?)</span>')
        lang = tds[2]
        qlty = tds[3]
        if not url or not servidor: continue

        itemlist.append(Item( channel = item.channel, action = 'play', server = servertools.corregir_servidor(servidor),
                              title = '', url = url, 
                              language = IDIOMAS.get(lang, lang), quality = qlty, quality_num = puntuar_calidad(qlty), other='d'
                       ))

    return itemlist



def list_search(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = re.compile('<li class="col-md-12 itemlist">(.*?)</li>', re.DOTALL).findall(data)

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)')
        title = scrapertools.find_single_match(article, ' title="([^"]+)')
        if not url or not title: continue
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        year = scrapertools.find_single_match(article, '<p class="main-info-list">Película de (\d{4})')
        if year:
            title = title.replace('(%s)' % year, '').strip()
        else:
            year = '-'
        plot = scrapertools.find_single_match(article, '<p class="text-list">(.*?)</p>')

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, 
                                    contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist

def search(item, texto):
    logger.info("texto: %s" % texto)
    try:
        item.url = HOST + '/search/' + texto.replace(" ", "+")
        return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
