# -*- coding: utf-8 -*-

import re, time

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb

host = 'https://cliver.site'


perpage = 30


def item_configurar_proxies(item):
    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = 'Configurar proxies a usar ...', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)


def do_downloadpage(url, post=None, headers=None):
    # ~ data = httptools.downloadpage(url, post=post, headers=headers).data
    data = httptools.downloadpage_proxy('cliversite', url, post=post, headers=headers).data

    if '<title>You are being redirected...</title>' in data:
        try:
            from lib import balandroresolver
            ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
            if ck_name and ck_value:
                # ~ logger.debug('Cookies: %s %s' % (ck_name, ck_value))
                httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])
                # ~ data = httptools.downloadpage(url, post=post, headers=headers).data
                data = httptools.downloadpage_proxy('cliversite', url, post=post, headers=headers).data
                # ~ logger.debug(data)
        except:
            pass

    return data


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series' ))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all' ))

    itemlist.append(item_configurar_proxies(item))
    return itemlist

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/peliculas', search_type = 'movie',
                                tipo = 'index', pagina = 1 ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + '/peliculas/estrenos', search_type = 'movie',
                                tipo = 'estrenos', pagina = 1 ))

    itemlist.append(item.clone( title = 'Más Vistas', action = 'list_all', url = host + '/peliculas/mas-vistas', 
                                search_type = 'movie', page = 0, pagina = 1 ))  

    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + '/peliculas/tendencias', 
                                search_type = 'movie', page = 0, pagina = 1 ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    itemlist.append(item_configurar_proxies(item))
    return itemlist

def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/series', search_type = 'tvshow',
                                tipo = 'index', pagina = 1 ))

    itemlist.append(item.clone( title = 'Series con nuevos capítulos', action = 'list_all', url = host + '/series/tendencias', 
                                search_type = 'tvshow', pagina = 1 ))

    itemlist.append(item.clone( title = 'Más Vistas', action = 'list_all', url = host + '/series/mas-vistas', 
                                search_type = 'tvshow', page = 0, pagina = 1 ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    itemlist.append(item_configurar_proxies(item))
    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    url = host if item.search_type == 'movie' else host + '/series'

    data = do_downloadpage(url)

    bloque = scrapertools.find_single_match(data, '<div class="generos">(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)">\s*<span class="cat">([^<]+)')

    for url, title in matches:
        if item.search_type == 'tvshow':
            url = url.replace('peliculas', 'series')

        url = host + url

        itemlist.append(item.clone( action="list_all", title=title, url=url, pagina = 1 ))

    return sorted(itemlist, key=lambda it: it.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    if item.search_type == 'movie': tope = 1938
    else: tope = 1949

    for ano in range(current_year, tope, -1):
        if item.search_type == 'movie':
            url = host + '/peliculas/anio/' + str(ano)
        else:
            url = host + '/series/anio/' + str(ano)

        itemlist.append(item.clone( action="list_all", title=str(ano), url=url, pagina = 1 ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    if item.search_type == 'movie':
        tipo_web = 'peliculas'
    elif item.search_type == 'tvshow':
        tipo_web = 'series'
    else:
        tipo_web = ''

    url_acceso = item.url
    if not '/search.html' in item.url:
        if not '?tipo=' in url_acceso:
            url_acceso = url_acceso + '?tipo=' + tipo_web
        if not '&page=' in url_acceso:
            url_acceso = url_acceso + '&page=' + str(item.pagina)

    data = do_downloadpage(url_acceso)

    # ~ logger.debug(data)

    if item.tipo == 'index':
       data = scrapertools.find_single_match(data, 'AGREGADAS(.*?)</section>')
    elif '/series/tendencias' in item.url:
       data = scrapertools.find_single_match(data, 'NUEVOS(.*?)</section>')
    elif '/search.html' in item.url:
       data = scrapertools.find_single_match(data, 'RESULTADOS(.*?)</section>')

    matches = re.compile('<article class="contenido-p">(.*?)</article>', re.DOTALL).findall(data)
    num_matches = len(matches)

    for article in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        url = host + url

        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        title = scrapertools.find_single_match(article, '<h2>(.*?)</h2>').strip()
        year = scrapertools.find_single_match(article, '<span>(\d{4})')
        if not year: year = '-'

        tipo_suf = 'movie' if '/pelicula/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo_suf

        if '/pelicula/' in url:
            if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, 
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))
        else:
            if item.search_type == 'movie': continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, 
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    # Subpaginación interna y/o paginación de la web
    buscar_next = True
    if num_matches > perpage: # subpaginación interna dentro de la página si hay demasiados items
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title='>> Página siguiente', page=item.page + 1, pagina = item.pagina, action='list_all', text_color='coral' ))
            buscar_next = False

    if buscar_next:
       if itemlist:
           if not item.tipo == 'estrenos':
               if not '/search.html' in item.url:
                   if item.tipo == 'index': tope = 12
                   else: tope = 18

                   if len(itemlist) >= tope:
                       pagina = item.pagina + 1
                       url = url_acceso.split('?tipo=')[0]
                       url = url + '?tipo=index' + '&page=' + str(pagina)

                       itemlist.append(item.clone( title = '>> Página siguiente', url = url, action = 'list_all', pagina = pagina, text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    patron ='<div class="menu-item " id="temporada(\d+)">'
    matches = re.compile(patron, re.DOTALL).findall(data)

    num_matches = len(matches)

    for numtempo in matches:
        title = 'Temporada ' + numtempo

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&'), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist

        if num_matches >= 10:
           if len(numtempo) == 1:
               nro_temp = '0' + numtempo
           else:
               nro_temp = numtempo

           title = 'Temporada ' + nro_temp

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = numtempo, page = 0 ))

    tmdb.set_infoLabels(itemlist)

    return sorted(itemlist, key=lambda it: it.title)

    #return itemlist

# Si una misma url devuelve los episodios de todas las temporadas, definir rutina tracking_all_episodes para acelerar el scrap en trackingtools.
def tracking_all_episodes(item):
    return episodios(item)

def episodios(item):
    logger.info()
    itemlist=[]

    if not item.page: item.page = 0
    perpage = 50

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    matches = re.compile('<div class="mic">(.*?)<i class="fa fa-play">', re.DOTALL).findall(data)

    for article in matches[item.page * perpage:]:
        season = scrapertools.find_single_match(article, 'data-season="([^"]+)')
        if not season: continue

        episode = scrapertools.find_single_match(article, 'data-ep="([^"]+)')
        plot = scrapertools.find_single_match(article, '<p><p style=".*?">(.*?)</p>').strip()

        if not item.contentSeason: continue
        elif not str(item.contentSeason) == season: continue

        if len(episode) == 1:
            nro_epi = '0' + episode
        else:
            nro_epi = episode

        titulo = season + 'x' + nro_epi + ' Episodio ' + episode
        url = item.url + '/' + season + '/' + episode

        itemlist.append(item.clone( action='findvideos', title = titulo, url = url, plot = plot,
                                    contentType = 'episode', contentSeason = season, contentEpisodeNumber = episode ))

        if len(itemlist) >= perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if len(matches) > ((item.page + 1) * perpage):
        itemlist.append(item.clone( title=">> Página siguiente", action="episodios", page=item.page + 1, text_color='coral' ))

    return sorted(itemlist, key=lambda it: it.title)


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'lat': 'Lat', 'es': 'Esp', 'vose': 'Vose', 'en': 'VO'}

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    matches_idiomas = scrapertools.find_multiple_matches(data, '<img src="/static/img/bg/icon_(.*?)_.*?data-id="(.*?)"')

    for lang, data_id in matches_idiomas:
        bloque_enlaces_idioma = scrapertools.find_single_match(data, 'server-item-(.*?)</div></div>')
        if not bloque_enlaces_idioma.startswith('</div>'):
            bloque_enlaces_idioma = bloque_enlaces_idioma + '</div>'

        enlaces = scrapertools.find_multiple_matches(bloque_enlaces_idioma, 'data-video="(.*?)".*?<img.*?>(.*?)</div>')

        for data_video, srv in enlaces:
            url = data_video
            if url.startswith('//'): url = 'https:' + url

            servidor = servertools.get_server_from_url(url)

            if servidor == 'directo':
                link_other = normalize_other(srv)
                if not link_other: continue
            else: link_other = ''

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url,
                                  language = IDIOMAS.get(lang, lang), other = link_other ))

    return itemlist


# Descartat hydrax pq de moment no es poden resoldre
def normalize_other(srv):
    srv = srv.replace('.to', '').lower()

    if srv == 'peliscloud': link_other = 'cloud'
    elif srv == 'damedamehoy': link_other = 'dame'
    elif srv == 'suppervideo': link_other = 'super'
    else:
       if config.get_setting('developer_mode', default=False): link_other = srv
       else: link_other = ''

    return link_other


def play(item):
    logger.info()
    itemlist = []

    servidor = item.server

    if item.other:
        if item.other == 'cloud':
            dom = '/'.join(item.url.split('/')[:3])
            vid = scrapertools.find_single_match(item.url, 'id=([^&]+)$')
            if not dom or not vid: return itemlist

            url = dom + '/playlist/' + vid + '/' + str(int(time.time() * 1000))
            data = httptools.downloadpage(url).data
            # ~ logger.debug(data)

            matches = scrapertools.find_multiple_matches(data, 'RESOLUTION=\d+x(\d+)\s*(.*?\.m3u8)')
            if matches:
                for res, url in sorted(matches, key=lambda x: int(x[0]), reverse=True):
                    itemlist.append(item.clone(url = dom + url, server = 'm3u8hls'))
                    break

            return itemlist

        elif item.other == 'dame':
            url = item.url.replace('https://damedamehoy.xyz/embed.html#', 'https://damedamehoy.xyz/details.php?v=')
            data = do_downloadpage(url)
            url = scrapertools.find_single_match(data, '"file":"(.*?)"')
            url = url.replace('\\/', '/')

            itemlist.append(item.clone(url=url , server=servidor))
            return itemlist

        elif item.other == 'super':
            data = do_downloadpage(item.url)

            matches = scrapertools.find_multiple_matches(data, 'data-video="(.*?)"')

            for url in matches:
                if 'https://damedamehoy.xyz/embed.html#' in url:
                    url = url.replace('https://damedamehoy.xyz/embed.html#', 'https://damedamehoy.xyz/details.php?v=')
                    data = do_downloadpage(url)

                    url = scrapertools.find_single_match(data, '"file":"(.*?)"')
                    url = url.replace('\\/', '/')
                    if url:
                        itemlist.append(item.clone(url=url , server=servidor))
                        return itemlist

                servidor = servertools.get_server_from_url(url)
                url = servertools.normalize_url(servidor, url)

                if servidor and servidor != 'directo':
                    itemlist.append(item.clone(url=url , server=servidor))
                    return itemlist

            return itemlist

        else:
            return itemlist
    else:
        url = item.url

    if url:
        itemlist.append(item.clone(url=url , server=servidor))

    return itemlist


def search(item, texto):
    logger.info()

    item.url = host + '/search.html?keyword=' + texto.replace(" ", "+")

    try:
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
