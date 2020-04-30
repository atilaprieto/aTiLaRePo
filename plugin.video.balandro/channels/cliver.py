# -*- coding: utf-8 -*-

import re

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, jsontools, servertools, tmdb

host = 'https://www.cliver.to/'


def item_configurar_proxies(item):
    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = 'Configurar proxies a usar ...', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)

def do_downloadpage(url, post=None, headers=None):
    # ~ data = httptools.downloadpage(url, post=post, headers=headers).data
    data = httptools.downloadpage_proxy('cliver', url, post=post, headers=headers).data
    return data


def mainlist(item):
    return mainlist_pelis(item)
    # ~ logger.info()
    # ~ itemlist = []

    # ~ itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis' ))
    # ~ itemlist.append(item.clone( title = 'Series', action = 'mainlist_series' )) # de momento las han quitado en la web

    # ~ itemlist.append(item_configurar_proxies(item))
    # ~ return itemlist

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Últimas películas', action = 'list_all', url = host + 'peliculas/', 
                                search_type = 'movie', tipo = 'index', pagina = 0 ))

    itemlist.append(item.clone( title = 'Películas de Estreno', action = 'list_all', url = host + 'peliculas/estrenos/', 
                                search_type = 'movie', tipo = 'estrenos', pagina = 0 ))

    itemlist.append(item.clone( title = 'Películas más Vistas', action = 'list_all', url = host + 'peliculas/mas-vistas/', 
                                search_type = 'movie', tipo = 'mas-vistas', pagina = 0 ))

    itemlist.append(item.clone( title = 'Películas Tendencia', action = 'list_all', url = host + 'peliculas/tendencias/', 
                                search_type = 'movie', tipo = 'peliculas-tendencias', pagina = 0 ))
    
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anyos', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    itemlist.append(item_configurar_proxies(item))
    return itemlist

def disabled_mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Últimas series', action = 'list_all', url = host + 'series/', 
                                search_type = 'tvshow', tipo = 'indexSeries', pagina = 0 ))

    itemlist.append(item.clone( title = 'Series más Vistas', action = 'list_all', url = host + 'series/mas-vistas/', 
                                search_type = 'tvshow', tipo = 'mas-vistas-series', pagina = 0 ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por cadena (network)', action = 'networks', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anyos', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'list_episodes', url = host + 'series/nuevos-capitulos/', 
                                search_type = 'tvshow', tipo = 'nuevos-capitulos', pagina = 0 ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    itemlist.append(item_configurar_proxies(item))
    return itemlist


def generos(item):
    logger.info()
    itemlist = []
    
    url = host if item.search_type == 'movie' else host + 'series/'
    data = do_downloadpage(url)
    
    bloque = scrapertools.find_single_match(data, '<div class="generos">(.*?)</ul>')
    
    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)">\s*<span class="cat">([^<]+)')
    for url, title in matches:
        adicional = scrapertools.find_single_match(url, '/genero/([^/]+)')
        tipo = 'genero' if item.search_type == 'movie' else 'generosSeries'
        itemlist.append(item.clone( action="list_all", title=title, url=url, tipo=tipo, adicional=adicional, pagina=0 ))

    return sorted(itemlist, key=lambda it: it.title)

def anyos(item):
    logger.info()
    itemlist = []
    
    url = host if item.search_type == 'movie' else host + 'series/'
    data = do_downloadpage(url)
    
    bloque = scrapertools.find_single_match(data, '<div class="anios">(.*?)</ul>')
    
    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)">([^<]+)')
    for url, title in matches:
        adicional = scrapertools.find_single_match(url, '/anio/([^/]+)')
        tipo = 'anio' if item.search_type == 'movie' else 'anioSeries'
        itemlist.append(item.clone( action="list_all", title=title, url=url, tipo=tipo, adicional=adicional, pagina=0 ))

    return itemlist

def networks(item):
    logger.info()
    itemlist = []
    
    data = do_downloadpage(host + 'series/')
    
    bloque = scrapertools.find_single_match(data, '<div class="networks">(.*?)</ul>')
    
    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)" class="[^"]*" title="([^"]+)')
    for url, title in matches:
        adicional = scrapertools.find_single_match(url, '/network/([^/]+)')
        itemlist.append(item.clone( action="list_all", title=title, url=url, tipo='networkSeries', adicional=adicional, pagina=0 ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []
    if not item.pagina: item.pagina = 0

    if item.pagina == 0 and item.tipo == 'buscador':
        data = do_downloadpage(item.url, headers={'Cookie': 'tipo_contenido=peliculas'})
    else:
        post = {'tipo': item.tipo, 'pagina': item.pagina}
        if item.adicional: post['adicional'] = item.adicional
        data = do_downloadpage(host+'frm/cargar-mas.php', post=post)
    # ~ logger.debug(data)

    matches = re.compile('<article class="contenido-p">(.*?)</article>', re.DOTALL).findall(data)
    for article in matches:

        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        title = scrapertools.find_single_match(article, '<h2>(.*?)</h2>').strip()
        year = scrapertools.find_single_match(article, '<span>(\d{4})')
        if not year: year = '-'

        if item.search_type == 'movie':
            langs = scrapertools.find_multiple_matches(article, '<div class="([^"]+)"></div>')
            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, 
                                        id_pelicula = scrapertools.find_single_match(thumb, '/(\d+)_min'),
                                        contentType='movie', contentTitle=title, infoLabels={'year': year},
                                        languages = ', '.join(langs) ))
        else:
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, 
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))
            
    tmdb.set_infoLabels(itemlist)

    num = 12 if item.tipo.startswith('index') else 18
    if len(matches) >= num:
        itemlist.append(item.clone( title='>> Página siguiente', pagina = item.pagina + 1, action='list_all' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    
    patron ='<div class="menu-item" id="temporada(\d+)">'
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
    color_lang = config.get_setting('list_languages_color', default='red')

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    matches = re.compile('<div class="mic">(.*?)<i class="fa fa-play">', re.DOTALL).findall(data)
    for article in matches:
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        plot = scrapertools.find_single_match(article, '<p>(.*?)</p>').strip()

        season = scrapertools.find_single_match(article, 'data-numtemp="([^"]+)')
        episode = scrapertools.find_single_match(article, 'data-numcap="([^"]+)')
        title = scrapertools.find_single_match(article, 'data-titulo="([^"]+)')

        if item.contentSeason and item.contentSeason != int(season):
            continue

        langs = []
        for opc in ['data-url-es', 'data-url-es-la', 'data-url-vose', 'data-url-en']:
            url = scrapertools.find_single_match(article, '%s="([^"]+)' % opc)
            if url: langs.append(opc.replace('data-url-', '').replace('es-la', 'lat'))
            # ~ logger.debug(url)

        if langs: title += ' [COLOR %s][%s][/COLOR]' % (color_lang, ', '.join(langs))
        
        itemlist.append(item.clone( action='findvideos', title = title, thumbnail=thumb, plot = plot,
                                    contentType = 'episode', contentSeason = season, contentEpisodeNumber = episode ))

    tmdb.set_infoLabels(itemlist)

    return itemlist

def list_episodes(item):
    logger.info()
    itemlist = []
    if not item.pagina: item.pagina = 0
    color_lang = config.get_setting('list_languages_color', default='red')

    post = {'tipo': item.tipo, 'pagina': item.pagina}
    data = do_downloadpage(host+'frm/cargar-mas.php', post=post)

    matches = re.compile('<article class="contenido-p">(.*?)</article>', re.DOTALL).findall(data)
    for article in matches:

        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        show = scrapertools.find_single_match(article, '<h2>(.*?)</h2>').strip()
        title = scrapertools.find_single_match(article, '<span>(.*?)</span>')
        langs = scrapertools.find_multiple_matches(article, '<div class="([^"]+)"></div>')
        
        s_e = scrapertools.find_single_match(url, '/(\d+)/(\d+)/')
        if not s_e: continue
        
        titulo = '%s - %s' % (show, title)
        if langs: titulo += ' [COLOR %s][%s][/COLOR]' % (color_lang, ', '.join(langs))

        itemlist.append(item.clone( action='findvideos', url=url, title=titulo, thumbnail=thumb, 
                                    contentType='episode', contentSerieName=show, contentSeason = s_e[0], contentEpisodeNumber = s_e[1] ))
            
    tmdb.set_infoLabels(itemlist)

    if len(matches) >= 18:
        itemlist.append(item.clone( title='>> Página siguiente', pagina = item.pagina + 1, action='list_episodes' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    
    IDIOMAS = {'es_la': 'Lat', 'es': 'Esp', 'vose': 'VOSE', 'en': 'VO'}

    if item.contentType == 'movie':
        if not item.id_pelicula:
            data = do_downloadpage(item.url)
            item.id_pelicula = scrapertools.find_single_match(data, 'Idpelicula\s*=\s*"([^"]+)')

        data = do_downloadpage(host + 'frm/obtener-enlaces-pelicula.php', post={'pelicula': item.id_pelicula})
        # ~ logger.debug(data)
        enlaces = jsontools.load(data)
        for lang in enlaces:
            for it in enlaces[lang]:
                # ~ servidor = 'directo' if it['reproductor_nombre'] == 'SuperVideo' else it['reproductor_nombre'].lower()
                servidor = 'directo' if it['reproductor_nombre'] in ['SuperVideo', 'FastPlayer'] else it['reproductor_nombre'].lower()
                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor,
                                      title = '', url = 'https://directv.clivertv.com/getFile.php?hash='+it['token'],
                                      language = IDIOMAS.get(lang, lang), other = it['reproductor_nombre'] if servidor == 'directo' else ''
                               ))

    else:
        data = do_downloadpage(item.url)
        # ~ logger.debug(data)
        data = scrapertools.find_single_match(data, 'data-numcap="%s" data-numtemp="%s"(.*?)>' % (item.contentEpisodeNumber, item.contentSeason))

        for opc in ['data-url-es', 'data-url-es-la', 'data-url-vose', 'data-url-en']:
            url = scrapertools.find_single_match(data, '%s="([^"]+)' % opc)
            if url:
                servidor = servertools.get_server_from_url(url)
                if not servidor or servidor == 'directo': continue
                lang = opc.replace('data-url-', '').replace('-', '_')
                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor,
                                      title = '', url = url,
                                      language = IDIOMAS.get(lang, lang)
                               ))

    return itemlist

def play(item):
    logger.info()
    itemlist = []

    if item.url.startswith('https://directv.clivertv.com/getFile.php'):
        url = item.url.split('?')[0]
        post = item.url.split('?')[1]
        data = httptools.downloadpage(url, post=post).data.replace('\\/', '/')
        # ~ logger.debug(data)
        try:
            dom, vid = scrapertools.find_single_match(data, '(https://[^/]+)/player/([^&]+)')
            # ~ url = '%s/hls/%s/i/%s.playlist.m3u8' % (dom, vid, vid)
            url = '%s/hls/%s/%s.m3u8' % (dom, vid, vid)
        except:
            url = scrapertools.find_single_match(data, '"url":"([^"]+)').replace(' ', '%20')
        
        if 'id=' in url:
            vid = scrapertools.find_single_match(url, 'id=([^&]+)')
            if vid:
                dom = '/'.join(url.split('/')[:3]) # SuperVideo: https://www.zembed.to FastPlayer: https://www.xtream.to
                url = dom + '/hls/' + vid + '/' + vid + '.playlist.m3u8'
                
                data = httptools.downloadpage(url).data
                # ~ logger.debug(data)
                matches = scrapertools.find_multiple_matches(data, 'RESOLUTION=\d+x(\d+)\s*(.*?\.m3u8)')
                if matches:
                    if 'xtream.to/' in url:
                        for res, url in sorted(matches, key=lambda x: int(x[0]), reverse=True):
                            itemlist.append(item.clone(url = dom + url, server = 'm3u8hls'))
                            break
                    else:
                        for res, url in sorted(matches, key=lambda x: int(x[0])):
                            itemlist.append([res+'p', dom + url])
                    return itemlist

            else:
                url = None
        
    else:
        url = item.url

    if url:
        itemlist.append(item.clone(url=url))
            
    return itemlist


def search(item, texto):
    logger.info()
    try:
        tipo = 'buscador' if item.search_type == 'movie' else 'buscadorSeries'
        return list_all(item.clone( pagina=0, tipo=tipo, adicional=texto.replace(" ", "+"), url=host+'buscar/?txt='+texto.replace(" ", "+") ))
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
