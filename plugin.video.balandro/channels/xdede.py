# -*- coding: utf-8 -*-

import re, urllib

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, jsontools, servertools, tmdb

# ~ host = 'https://xdede.co/'
host = 'https://movidy.co/'


def do_downloadpage(url, post=None, headers=None):
    url = url.replace('https://xdede.co/', 'https://movidy.co/') # por si viene de enlaces guardados
    data = httptools.downloadpage(url, post=post, headers=headers).data
    # ~ data = httptools.downloadpage_proxy('xdede', url, post=post, headers=headers).data
    return data


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series' ))

    itemlist.append(item.clone( title = 'Listas de películas y series', action = 'list_lists', url = host + 'listas' ))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all' ))

    return itemlist

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Últimas películas', action = 'list_all', url = host + 'peliculas' ))
    itemlist.append(item.clone( title = 'Películas de estreno', action = 'list_all', url = host + 'peliculas/estrenos' ))
    itemlist.append(item.clone( title = 'Películas más valoradas', action = 'list_all', url = host + 'peliculas/mejor-valoradas' ))
    itemlist.append(item.clone( title = 'Películas actualizadas', action = 'list_all', url = host + 'actualizado/peliculas' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anyos', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Listas de películas y series', action = 'list_lists', url = host + 'listas' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist

def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Últimas series', action = 'list_all', url = host + 'series' ))
    itemlist.append(item.clone( title = 'Series más valoradas', action = 'list_all', url = host + 'series/mejor-valoradas' ))
    itemlist.append(item.clone( title = 'Series actualizadas', action = 'list_all', url = host + 'actualizado/series' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anyos', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Listas de películas y series', action = 'list_lists', url = host + 'listas' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []
    
    url_base = host + ('peliculas' if item.search_type == 'movie' else 'series') + '/filtro/'

    # ~ data = do_downloadpage(host+'static/js/dddTest25.js')
    data = do_downloadpage(host+'static/js/javas.js')
    
    bloque = scrapertools.find_single_match(data, '<ul class="Ageneros">(.*?)</ul>')
    
    matches = scrapertools.find_multiple_matches(bloque, '<b>([^<]+)</b></li>')
    for title in matches:
        url = url_base + title + ',/,'
        itemlist.append(item.clone( action="list_all", title=title, url=url ))

    if item.search_type == 'tvshow':
        itemlist.append(item.clone( action="list_all", title='Anime', url=host + 'animes' ))
        
    return sorted(itemlist, key=lambda it: it.title)

def anyos(item):
    logger.info()
    itemlist = []
    
    url_base = host + ('peliculas' if item.search_type == 'movie' else 'series') + '/filtro/'

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1984, -1):
        url = url_base + ',/' + str(x) + ','
        itemlist.append(item.clone( action='list_all', title=str(x), url=url ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []
    
    es_busqueda = 'search?' in item.url
    es_lista = '/listas/' in item.url
    tipo_url = 'tvshow' if '/series' in item.url or '/animes' in item.url else 'movie'

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)
    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        thumb = scrapertools.find_single_match(article, ' data-echo="([^"]+)"')
        title = scrapertools.find_single_match(article, ' title="([^"]+)"').strip()
        if not url or not title: continue

        tid = scrapertools.find_single_match(url, '(\d+)-')
        if tid:
            infoLabels = {'tmdb_id':tid, 'year': '-'}
        else:
            infoLabels = {'year': '-'}

        if es_busqueda or es_lista:
            tipo = 'tvshow' if '/series' in url or '/animes' in url else 'movie'
            if item.search_type not in ['all', tipo]: continue
        else:
            tipo = tipo_url
        
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            qlty = 'Low' if 'CALIDAD BAJA' in article else ''
            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels=infoLabels ))
        else:
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=title, infoLabels=infoLabels ))

            
    tmdb.set_infoLabels(itemlist)

    next_page_link = scrapertools.find_single_match(data, '<a href="([^"]+)"[^>]*>Pagina siguiente')
    if next_page_link:
        itemlist.append(item.clone( title='>> Página siguiente', url=next_page_link, action='list_all' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    
    patron = ' onclick="activeSeason\(this,\'temporada-(\d+)'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for numtempo in matches:
        itemlist.append(item.clone( action='episodios', title='Temporada %s' % numtempo,
                                    contentType='season', contentSeason=numtempo ))
        
    tmdb.set_infoLabels(itemlist)

    return itemlist

# Si una misma url devuelve los episodios de todas las temporadas, definir rutina tracking_all_episodes para acelerar el scrap en trackingtools.
def tracking_all_episodes(item):
    return episodios(item)

def episodios(item):
    logger.info()
    itemlist=[]

    data = do_downloadpage(item.url)

    patron = '<li\s*><a href="([^"]+)"\s*up-modal=".Flex"><div class="wallEp"(.*?)</li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, datos in matches:
        try:
            season, episode = scrapertools.find_single_match(url, '/(\d+)x(\d+)$')
        except:
            continue

        if item.contentSeason and item.contentSeason != int(season):
            continue

        title = scrapertools.find_single_match(datos, '<h2>(.*?)</h2>')
        thumb = scrapertools.find_single_match(datos, ' data-echo="([^"]+)"')
        titulo = '%sx%s %s' % (season, episode, title)

        itemlist.append(item.clone( action='findvideos', title = titulo, thumbnail=thumb, url = url,
                                    contentType = 'episode', contentSeason = season, contentEpisodeNumber = episode ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


# Asignar un numérico según las calidades del canal, para poder ordenar por este valor
def puntuar_calidad(txt):
    orden = ['360p', '480p', '720p', '1080p']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1

def findvideos(item):
    logger.info()
    itemlist = []
    
    IDIOMAS = {'1': 'Esp', '2': 'Lat', '3': 'VOSE', '4': 'VO'}

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    # Enlaces oficiales
    try:
        x = scrapertools.find_single_match(data, '\s*secid="([^"]+)"\s*wallp="([^"]*)"\s*vip1080p="([^"]*)"\s*sBay="([^"]*)"\s*BotU="([^"]*)"')
        if not x or len(x) != 5: raise()
        post = {'id': x[0], 'wall': x[1], 'v1080': x[2], 'botu': x[4], 'sBay': x[3]}
        
        data2 = do_downloadpage(host + 'json/loadVIDEOSV4', post=urllib.urlencode(post))
        # ~ logger.debug(data2)
        jdata = jsontools.load(data2)
        data2 = jdata['result'].replace("\'", "'")
        # ~ logger.debug(data2)
        
        for numlang in IDIOMAS:
            bloque = scrapertools.find_single_match(data2, '<div class="OD_%s(.*?)</div>' % numlang)
            if not bloque: continue
            enlaces = scrapertools.find_multiple_matches(bloque, "<li onclick=\"\w+\('([^']+)'(.*?)</li>")
            for enlace, resto in enlaces:
                other = ''
                servidor = scrapertools.find_single_match(resto, '<span>(.*?)</span>')
                servidor = servertools.corregir_servidor(servidor)
                if servidor == 'pro': servidor = 'fembed'
                elif servidor in ['bot','soap']:
                    other = servidor.capitalize()
                    servidor = 'directo'

                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor,
                                      title = '', url = enlace, referer = item.url,
                                      language = IDIOMAS.get(numlang, 'VO'), other = other
                               ))
    except:
        pass

    # Enlaces de usuarios (desactivado por requerir recaptcha)
    # ~ if '<div class="linksUsers">' in data:
        # ~ enlaces = scrapertools.find_multiple_matches(data.split('<div class="linksUsers">')[1], '<li(.*?)</li>')
        # ~ for enlace in enlaces:
            # ~ url = scrapertools.find_single_match(enlace, ' href="([^"]+)"')
            # ~ numlang = scrapertools.find_single_match(enlace, '/img/(\d+)\.png')
            # ~ servidor = scrapertools.find_single_match(enlace, '\?domain=([^.]+)')
            # ~ servidor = servertools.corregir_servidor(servidor)
            # ~ if not servidor and 'powvideo.net' in enlace: servidor = 'powvideo'
            # ~ qlty = scrapertools.find_single_match(enlace, '<b>(.*?)</b>')
            # ~ user = scrapertools.find_single_match(enlace, 'user/([^"]+)')

            # ~ itemlist.append(Item( channel = item.channel, action = 'play', server = servidor,
                                  # ~ title = '', url = url, referer = item.url,
                                  # ~ language = IDIOMAS.get(numlang, 'VO'), 
                                  # ~ quality = qlty, quality_num = puntuar_calidad(qlty), other = user
                           # ~ ))

    return itemlist

def play(item):
    logger.info()
    itemlist = []

    if item.url.startswith(host):
        headers = { 'Referer': item.referer }

        if not '/encrypt/' in item.url: # acceder al json y extraer link /encrypt/...
            data = do_downloadpage(item.url, headers=headers)
            # ~ logger.debug(data)
            jdata = jsontools.load(data)
            if 'status' in jdata and str(jdata['status']) != '200': return 'El vídeo no está disponible'
            if 'mp4' in jdata:
                item.url = jdata['mp4'].replace('\\/', '/')
            elif 'data' in jdata:
                if type(jdata['data']) is dict:
                    if 'data' not in jdata['data']: return 'No se encuentra el vídeo'
                    item.url = jdata['data']['data']
                else:
                    item.url = jdata['data']
            else:
                return 'El vídeo no se encuentra'
            if not item.url.startswith('http'): item.url = host + 'encrypt/' + item.url

        # extraer de link /encrypt/
        resp = httptools.downloadpage(item.url, headers=headers, follow_redirects=False)

        if 'refresh' in resp.headers:
            url = scrapertools.find_single_match(resp.headers['refresh'], ';\s*(.*)')

        elif 'location' in resp.headers:
            url = resp.headers['location']

        else:
            # ~ logger.debug(resp.data)
            url = None
            bloque = scrapertools.find_single_match(resp.data, '"sources":\s*\[(.*?)\]')
            if not bloque: return 'No se encuentran fuentes para este vídeo'
            for enlace in scrapertools.find_multiple_matches(bloque, "\{(.*?)\}"):
                v_url = scrapertools.find_single_match(enlace, '"file":\s*"([^"]+)')
                if not v_url: continue
                v_lbl = scrapertools.find_single_match(enlace, '"label":\s*"([^"]+)')
                if not v_lbl: v_lbl = scrapertools.find_single_match(enlace, '"type":\s*"([^"]+)')
                if not v_lbl: v_lbl = 'mp4'
                itemlist.append([v_lbl, v_url])

            if len(itemlist) > 1:
                return sorted(itemlist, key=lambda x: int(x[0]) if x[0].isdigit() else 0)
                
        if url:
            url = url.replace('https://www.privatecrypt.me/', 'https://www.fembed.com/')
            servidor = servertools.get_server_from_url(url)
            if servidor and servidor != 'directo':
                url = servertools.normalize_url(servidor, url)
                itemlist.append(item.clone( url=url, server=servidor ))

    else:
        itemlist.append(item.clone())

    return itemlist




def search(item, texto):
    logger.info("texto: %s" % texto)
    try:
        item.url = host + 'search?go=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []



def list_lists(item):
    logger.info()
    itemlist = []
    
    data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)
    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        title = scrapertools.find_single_match(article, '<h2>(.*?)</h2>').strip()
        plot = scrapertools.find_single_match(article, '<p>(.*?)</p>').strip()
        if not url or not title: continue

        itemlist.append(item.clone( action="list_all", title=title, url=url, plot=plot, search_type='all' ))

    next_page_link = scrapertools.find_single_match(data, '<a href="([^"]+)"[^>]*>Pagina siguiente')
    if next_page_link:
        itemlist.append(item.clone( title='>> Página siguiente', url=next_page_link, action='list_lists' ))

    return itemlist
