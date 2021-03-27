# -*- coding: utf-8 -*-

import re

from platformcode import logger
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://pelisretro.com/'

perpage = 20


def mainlist(item):
    return mainlist_pelis(item)

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'listado/' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action='alfabetico' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    for letra in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        letras = letra.lower()

        url = host + 'letter/' + letras + '/'

        itemlist.append(item.clone( action = 'list_alfa', title = letra, url = url ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    bloque = scrapertools.find_single_match(data, '<a>Genero</a>(.*?)</ul>')
    patron = 'class="menu-item menu-item-type-taxonomy menu-item-object-category.*?<a href="([^"]+)">(.*?)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for url, title in matches:
        itemlist.append(item.clone( action = "list_all", title = title, url = url ))

    return sorted(itemlist, key=lambda it: it.title)


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)
    num_matches = len(matches)

    for data_show in matches[item.page * perpage:]:
        title = scrapertools.find_single_match(data_show, '<h3 class="Title">(.*?)</h3>')

        thumb = scrapertools.find_single_match(data_show, 'data-src="([^"]+)"')
        if not thumb: thumb = scrapertools.find_single_match(data_show, '<img src="([^"]+)"')
        if thumb.startswith('//'): thumb = 'https:' + thumb

        url = scrapertools.find_single_match(data_show, '<a href="([^"]+)"')

        year = scrapertools.find_single_match(data_show, '<span class="Year">(.*?)</span>')
        if not year: year = '-'

        name = title.replace('&#038;', '&')

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, 
                                    contentType = 'movie', contentTitle = name, infoLabels = {'year': year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    buscar_next = True
    if num_matches > perpage:
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title = '>> Página siguiente', page = item.page + 1, action='list_all', text_color='coral' ))
            buscar_next = False

    if buscar_next:
        if '<div class="wp-pagenavi">' in data:
            next_page = scrapertools.find_single_match(data, '<div class="wp-pagenavi">.*?<a class="next page-numbers" href="([^"]+)"')
            if next_page:
                itemlist.append(item.clone( action = 'list_all', page = 0, url = next_page, title = '>> Página siguiente', text_color='coral' ))

    return itemlist


def list_alfa(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<td><span class="Num">(.*?)</tr>')
    num_matches = len(matches)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="([^"]+)')
        title = scrapertools.find_single_match(match, '<strong>(.*?)</strong>').strip()
        if not url or not title: continue

        if '/aplicacion-oficial-de-pelisretro-com/' in url: continue

        thumb = scrapertools.find_single_match(match, ' data-src="([^"]+)')

        year = scrapertools.find_single_match(match, '<strong>.*?<td>(\d{4})</td>')
        if not year: year = '-'

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, 
                                    contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, 'data-tplayernv="Opt(.*?)"><span>(.*?)</span>')

    for opt, servidor in matches:
        servidor = servidor.replace('<strong>', '').replace('</strong>', '')
        servidor = servertools.corregir_servidor(servidor)

        url = scrapertools.find_single_match(data, ' id="Opt' + str(opt) + '.*?src="([^"]+)"')
        if url.startswith('//') == True:
            url = scrapertools.find_single_match(data, ' id="Opt' + str(opt) + '.*?src=&quot;(.*?)&quot;')

        if not servidor or not url: continue

        if 'opción' in servidor:
            link_other = servidor
            servidor = 'directo'
        elif servidor == 'anavids':
            link_other = servidor
            servidor = 'directo'
        else: link_other = ''

        itemlist.append(Item( channel = item.channel, action = 'play', url = url, server = servidor, title = '',  language = 'Lat', other = link_other ))

    # Descargas
    matches = scrapertools.find_multiple_matches(data, '<td><span class="Num">(.*?)</tr>')

    for match in matches:
        servidor = scrapertools.find_single_match(match, 'alt="Descargar(.*?)">')
        servidor = servidor.replace('.', '').strip()

        if not servidor: continue

        servidor = servertools.corregir_servidor(servidor)

        url = scrapertools.find_single_match(match, ' href="(.*?)"')

        itemlist.append(Item( channel = item.channel, action = 'play', url = url, server = servidor, title = '',  language = 'Lat', other = 'd' ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url.replace('&amp;#038;', '&').replace('&#038;', '&').replace('&amp;', '&')

    if url.startswith(host):
        if item.other == 'd':
            url = httptools.downloadpage(url, follow_redirects=False, only_headers=True).headers.get('location', '')

            if url.startswith('https://ouo.io/'):
                if not '/go/' in url:
                    url = url.replace('https://ouo.io/', 'https://ouo.io/go/')

                ouo_code = url.replace('https://ouo.io/go/', '')
                headers = {'Referer': url.replace('/go/', '/')}

                data = httptools.downloadpage(url).data

                _action, _id, _token = scrapertools.find_single_match(data, '<form method="POST" action="(.*?)".*?id="(.*?)".*?name="_token" type="hidden" value="(.*?)"')
                post = {'action': _action, 'id': _id, '_token': _token }
                datos_post = httptools.downloadpage(url, post = post, headers = headers).data

                try:
                   _action2, _id2, _token2 = scrapertools.find_single_match(datos_post, '<form method="POST" action="(.*?)".*?id="(.*?)".*?name="_token" type="hidden" value="(.*?)"')
                   if _action2:
                       if not _action2 == _action:
                           headers = {'Referer': url}
                           if ouo_code in _action2: url = _action2
                           _action = _action2
                           _id = _id2
                           _token = _token2
                except:
                   pass
 
                post = {'action': _action, 'id': _id, '_token': _token }

                url = httptools.downloadpage(url, post = post, headers = headers, follow_redirects=False, only_headers=True).headers.get('location', '')

        else:
            data = httptools.downloadpage(url).data
            if item.other == 'anavids':
                url = scrapertools.find_single_match(data, '<IFRAME SRC="(.*?)"')

                data = httptools.downloadpage(url).data
                url = scrapertools.find_single_match(str(data), 'sources.*?"(.*?)"')
            else:
                url = scrapertools.find_single_match(data, 'src="([^"]+)"')

    if url:
        if url.startswith('//') == True: url = 'https:' + url

        servidor = servertools.get_server_from_url(url)
        if servidor:
            url = servertools.normalize_url(servidor, url)
            itemlist.append(item.clone(url = url, server = servidor))

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
