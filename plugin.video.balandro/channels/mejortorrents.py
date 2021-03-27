# -*- coding: utf-8 -*-

import re

from platformcode import logger
from core.item import Item
from core import httptools, scrapertools, tmdb


host = 'https://www.mejortorrents1.net'


selecc_pelis = host + '/peliculas-buscador.html'

perpage = 30


# ~ def item_configurar_proxies(item):
    # ~ plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    # ~ plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    # ~ return item.clone( title = 'Configurar proxies a usar ...', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )

# ~ def configurar_proxies(item):
    # ~ from core import proxytools
    # ~ return proxytools.configurar_proxies_canal(item.channel, host)


def do_downloadpage(url, post=None):
    data = httptools.downloadpage(url, post=post).data
    # ~ data = httptools.downloadpage_proxy('mejortorrents', url, post=post).data
    # ~ logger.debug(data)

    return data


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series' ))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all' ))

    # ~ itemlist.append(item_configurar_proxies(item))
    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/torrents-de-peliculas.html', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Últimas', action = 'list_last', url = host + '/secciones.php?sec=ultimos_torrents', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'En HD', action = 'list_all', url = host + '/torrents-de-peliculas-hd-alta-definicion.html', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Las más vistas', action = 'list_selecc', url = selecc_pelis, down = 100, search_type = 'movie' ))

    itemlist.append(item.clone( action ='generos', title = 'Por género', search_type = 'movie' ))
    itemlist.append(item.clone( action ='anios', title = 'Por año', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'alfabetico', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    # ~ itemlist.append(item_configurar_proxies(item))
    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/torrents-de-series.html', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimas', action = 'list_last', url = host + '/secciones.php?sec=ultimos_torrents', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En HD', action = 'list_all', url = host + '/torrents-de-series-hd-alta-definicion.html', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'alfabetico', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Documentales', action = 'list_all', url = host + '/torrents-de-documentales.html', search_type = 'documentary' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    # ~ itemlist.append(item_configurar_proxies(item))
    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    opciones = [
        'Acción',
        'Animación',
        'Aventuras',
        'Bélica',
        'Biográfica',
        'Ciencia ficción',
        'Cine Negro',
        'Comedia',
        'Crimen',
        'Documental',
        'Drama',
        'Fantasía',
        'Músical',
        'Romántica',
        'Suspense',
        'Terror',
        'Western'
        ]

    for opc in opciones:
        itemlist.append(item.clone( title = opc, url = selecc_pelis, action = 'list_selecc', genre = str(opc) ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1919, -1):
        itemlist.append(item.clone( title = str(x), url = selecc_pelis, action = 'list_selecc', anyo = str(x) ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, r'href="([^"]+)">([^<]+)</a>.*?<b>(.*?)<')
    num_matches = len(matches)

    for url, title, qlty in matches[item.page * perpage:]:
        titulo = title.split('-')[0].strip()
        title = re.sub(r' \(.*?\)', '', title)

        qlty = qlty.replace('(', '').replace(')', '').strip()

        thumb = scrapertools.find_single_match(data, url + '.*?<img src="(.*?)"')
        if not thumb.startswith('/'): thumb = '/' + thumb
        thumb = host + thumb

        if not url.startswith('/'): url = '/' + url
        url = host + url

        if item.search_type == 'movie':
            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty,
                                        contentType='movie', contentTitle=titulo, infoLabels={'year': '-'} ))
        else:
            if item.search_type == 'documentary': qlty = qlty.replace('Páginas:', '')

            itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb, qualities=qlty,
                                        contentType='tvshow', contentSerieName=titulo, infoLabels={'year': '-'} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    buscar_next = True
    if num_matches > perpage:
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title = '>> Página siguiente', page = item.page + 1, action='list_all', text_color='coral' ))
            buscar_next = False

    if buscar_next:
        next_page = scrapertools.find_single_match(data, "href='([^']+)'.class='paginar'>.Siguiente")
        if next_page:
            next_page = next_page.replace('&amp;', '&')

            if not next_page.startswith('/'): next_page = '/' + next_page
            next_page = host + next_page

            itemlist.append(item.clone( title='>> Página siguiente', page = 0, action='list_all', url=next_page, text_color='coral' ))

    return itemlist


def list_last(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if item.search_type == 'movie':
        fin_movies = 'SERIES' if 'SERIES' in data else 'JUEGOS'
        if fin_movies == 'JUEGOS' and not 'JUEGOS' in data:
            fin_movies = '<footer>'

        data = scrapertools.find_single_match(data, r'PELÍCULAS(.*?)' + fin_movies)
    else:
        fin_tvshows = 'JUEGOS' if 'JUEGOS' in data else '<footer>'
        data = scrapertools.find_single_match(data, r'SERIES(.*?)' + fin_tvshows)

    matches = scrapertools.find_multiple_matches(data, r"href='([^']+)'.*?>(.*?)<.*?'>(.*?)<")

    for url, title, qlty in matches:
        titulo = title.split('-')[0].strip()
        title = re.sub(r' \(.*?\)', '', title)

        if not url.startswith('/'): url = '/' + url
        url = url.replace('&amp;', '&')
        url = host + url

        qlty = qlty.replace('(', '').replace(')', '').strip()

        if item.search_type == 'movie':
            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, qualities = qlty, 
                                       contentType = 'movie', contentTitle = titulo, infoLabels = {'year': '-'} ))
        else:
            itemlist.append(item.clone( action='episodios', url = url, title = title,  qualities = qlty,
                                        contentType = 'tvshow', contentSerieName = titulo, infoLabels = {'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    if item.search_type == 'tvshow':
        url_series = host + '/series-letra-'

    for letra in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        if item.search_type == 'tvshow':
            url = url_series + letra.lower() + '.html'
            itemlist.append(item.clone( title = letra, action = 'list_selecc', url = url ))
        else:
            itemlist.append(item.clone( title = letra, action = 'list_selecc', url = selecc_pelis, letra = letra ))

    return itemlist


def list_selecc(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    if item.search_type == 'movie':
        headers = {'Referer': host + '/torrents-de-peliculas.html'}

        if item.letra:
            post = 'campo=letra&valor=&valor2=&valor3=' + str(item.letra) + '&valor4=3&submit=Buscar'
        elif item.anyo:
            post = 'campo=anyo&valor=' + str(item.anyo) + '&valor2=&valor3=&valor4=3&submit=Buscar'
        elif item.genre:
            post = 'campo=genero&valor=&valor2=' + str(item.genre) + '&valor3=&valor4=3&submit=Buscar'
        else:
            post = 'campo=contador_total&valor=' + str(item.down) + '&valor2=&valor3=&valor4=3&submit=Buscar'

        data = httptools.downloadpage(item.url, post=post, headers=headers).data
    else:
        data = httptools.downloadpage(item.url).data

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = r"href='([^']+)'.*?>(.*?)<"

    if item.search_type == 'movie':
        data = scrapertools.find_single_match(data, r'Has buscado(.*?)<footer>')
    else:
        data = scrapertools.find_single_match(data, r'Mostrando(.*?)<footer>')

    matches = scrapertools.find_multiple_matches(data, patron)
    num_matches = len(matches)

    for url, title in matches[item.page * perpage:]:
        titulo = title.split('-')[0].strip()
        title = re.sub(r' \(.*?\)', '', title)
        if not title: continue

        if not url.startswith('/'): url = '/' + url
        url = url.replace('&amp;', '&')
        url = host + url

        if item.search_type == 'movie':
            refer = scrapertools.find_single_match(url, '/peli-descargar-torrent-(.*?)-')

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, qualities = refer,
                                       contentType = 'movie', contentTitle = titulo, infoLabels = {'year': '-'} ))
        else:
            itemlist.append(item.clone( action='episodios', url = url, title = title, grupo = 'selecc',
                                        contentType = 'tvshow', contentSerieName = titulo, infoLabels = {'year': '-'} ))

        if len(itemlist) >= perpage: break

    if num_matches > perpage:
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title = '>> Página siguiente', page = item.page + 1, action='list_selecc', text_color='coral' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


# Asignar un numérico según las calidades del canal, para poder ordenar por este valor
def puntuar_calidad(txt):
    txt = txt.lower().replace(' ', '').replace('-', '')

    orden = [
      '3d',
      'screener',
      'dvdscr',
      'brscreener',
      'dvdscreener',
      'brscreener',
      'sd',
      'dvdrip',
      'rhdtv',
      'hdrip',
      'hdtv',
      '720p',
      'bluray720p',
      'microhd720p',
      '1080p',
      'fullbluray',
      '4khdr',
      '4k'
      ]

    if txt not in orden: return 0
    else: return orden.index(txt) + 1


def episodios(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    if item.search_type == 'documentary':
         bloque = scrapertools.find_single_match(data, 'Listado de los episodios(.*)Marcar/Desmarcar Todos')
    else:
         bloque = scrapertools.find_single_match(data, 'Listado de los episodios(.*)Descargar Seleccionados')

    matches = scrapertools.find_multiple_matches(bloque, "<a href='([^']+)'>(.*?)<")

    for url, title in matches:
        if not url.startswith('/'): url = '/' + url
        url = url.replace('&amp;', '&')
        url = host + url

        if item.grupo == 'selecc': title = title + '  ' + item.title

        itemlist.append(item.clone( action='findvideos', url = url, title = title ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    url = ''

    data = httptools.downloadpage(item.url).data

    if item.search_type == 'movie':
        data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;|<br>', '', data)
        patron = r"<img border=.*?src='([^']+).*?<b>Formato:?</b>:?\s*([^<]+).*?<b>Torrent.*?href='([^']+)"

        try:
           thumb, qlty, url = scrapertools.find_single_match(data, patron)
        except:
           return itemlist
    else:
        new_url = scrapertools.find_single_match(data, "<b>Torrent.*?<a href='([^']+)'")
        if new_url:
            url = new_url

            if not new_url.startswith('/'): new_url = '/' + new_url
            new_url = new_url.replace('&amp;', '&')
            new_url = host + new_url

            data = httptools.downloadpage(new_url).data

            qlty = item.qualities

    if url:
        if not url.startswith('/'): url = '/' + url

        try:
           data = httptools.downloadpage(host + url).data
           url_t = scrapertools.find_single_match(data, r"name: '([^']+)")
           if not url_t: url_t = scrapertools.find_single_match(data, "Pincha <a href='([^']+)")
        except:
           return itemlist

        tag = ''
        if not '/tor/peliculas/' in url_t and not '/tor/series/' in url_t:
            tag = '/tor/peliculas/' if item.search_type == 'movie' else '/tor/series/'

        url_torrent = host + tag + url_t

        size = scrapertools.find_single_match(data, r'Tamaño:</b>(.*?)<').replace(',', '.')

        if not '.' in size: size = ''
        if size:
            n = float(scrapertools.find_single_match(size, '(\d[.\d]*)')) * 1024
            size = n * 1024 if 'gb' in size.lower() else n

        lang = 'Esp'

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url_torrent, server = 'torrent',
                              language = lang, quality = qlty, quality_num = puntuar_calidad(qlty), other = size ))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = r"href='([^']+)'.*?>(.*?)<"

    data = scrapertools.find_single_match(data, r'Has realizado una búsqueda(.*?)<footer>')
    patron = r"href='([^']+)'.*?>(.*?)</a>.*?'>(.*?)<.*?<td.*?>(.*?)<"

    matches = scrapertools.find_multiple_matches(data, patron)
    num_matches = len(matches)

    for url, title, qlty, type in matches[item.page * perpage:]:
        if not type == 'Película' and not type == 'Serie' and not type == 'Documental': continue

        if item.search_type != 'all':
            if item.search_type == 'movie':
                if type == 'Serie': continue
                elif type == 'Documental': continue
            else:
                if type == 'Película': continue

        sufijo = ''

        if item.search_type == 'all':
            if type == 'Película': sufijo = 'movie'
            elif type == 'Serie': sufijo = 'tvshow'
            else: sufijo = 'documentary'

        title = title.replace("<font Color='darkblue'>", '').replace('</font>', '').replace("<span style='color:gray;'>", '').replace('</span>', '').strip()

        titulo = title.split('-')[0].strip()
        title = re.sub(r' \(.*?\)', '', title)

        if not url.startswith('/'): url = '/' + url
        url = url.replace('&amp;', '&')
        url = host + url

        qlty = qlty.replace('(', '').replace(')', '').strip()

        if item.search_type == 'movie':
            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, qualities = qlty, fmt_sufijo = sufijo,
                                       contentType = 'movie', contentTitle = titulo, infoLabels = {'year': '-'} ))
        else:
            itemlist.append(item.clone( action='episodios', url = url, title = title, qualities = qlty, fmt_sufijo = sufijo,
                                        contentType = 'tvshow', contentSerieName = titulo, infoLabels = {'year': '-'} ))

        if len(itemlist) >= perpage: break

    if num_matches > perpage:
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title = '>> Página siguiente', page = item.page + 1, action='list_search', text_color='coral' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def search(item, texto):
    logger.info("texto: %s" % texto)
    try:
        item.url = host + '/secciones.php?sec=buscador&valor=' + texto.replace(" ", "+")
        return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
