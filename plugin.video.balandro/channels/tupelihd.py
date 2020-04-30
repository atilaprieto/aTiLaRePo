# -*- coding: utf-8 -*-

import re

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools

host = 'https://www.tupelihd.com/'

IDIOMAS = {'Español':'Esp', 'Latino':'Lat', 'Subtitulado':'VOSE'}


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Películas', action = 'mainlist_pelis' ))
    itemlist.append(item.clone ( title = 'Series', action = 'mainlist_series' ))

    itemlist.append(item.clone ( title = 'Buscar ...', action = 'search', search_type = 'all' ))

    return itemlist

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Últimas películas', action = 'list_all', url = host + 'todas-las-peliculas/', search_type = 'movie' ))
    itemlist.append(item.clone ( title = 'Más votadas', action = 'list_all', url = host + 'mas-votadas/', search_type = 'movie' ))
    itemlist.append(item.clone ( title = 'Más vistas', action = 'list_all', url = host + 'peliculas-mas-vistas/', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Estrenos 2020', action = 'list_all', url = host + 'peliculas/estrenos-2020/', search_type = 'movie' ))
    itemlist.append(item.clone ( title = 'Estrenos 2019', action = 'list_all', url = host + 'peliculas/estrenos-2019/', search_type = 'movie' ))
    itemlist.append(item.clone ( title = 'Estrenos 2018', action = 'list_all', url = host + 'peliculas/estrenos-2018/', search_type = 'movie' ))

    itemlist.append(item.clone ( title = '4K UHD Micro', action = 'list_all', url = host + 'peliculas/4k-uhdmicro/', search_type = 'movie' ))
    itemlist.append(item.clone ( title = '4K UHD Rip', action = 'list_all', url = host + 'peliculas/4k-uhdrip/', search_type = 'movie' ))
    itemlist.append(item.clone ( title = 'Bluray MicroHD', action = 'list_all', url = host + 'peliculas/bluray-microhd/', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone ( title = 'Por países', action = 'paises', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist

def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Últimas series', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))
    itemlist.append(item.clone ( title = 'Más votadas', action = 'list_all', url = host + 'mas-votadas/', search_type = 'tvshow' ))
    itemlist.append(item.clone ( title = 'Más vistas', action = 'list_all', url = host + 'peliculas-mas-vistas/', search_type = 'tvshow' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    itemlist.append(item.clone ( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []
    
    data = httptools.downloadpage(host).data
    
    bloque = scrapertools.find_single_match(data, 'Generos</span></a>\s*<ul class="sub-menu">(.*?)</ul>')
    
    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)"><i[^>]*></i><span>([^<]+)')
    for url, title in matches:
        if '/estrenos/' in url: continue
        itemlist.append(item.clone( action='list_all', title=title, url=url ))

    return itemlist

def paises(item):
    logger.info()
    itemlist = []
    
    data = httptools.downloadpage(host).data
    
    matches = scrapertools.find_multiple_matches(data, '/country/([^/]+)/">([^<]+)</a></li>')
    for url, title in matches:
        itemlist.append(item.clone( action='list_all', title=title + ' - ' + url, url=host + 'country/' + url + '/' ))

    return sorted(itemlist, key=lambda it: it.title)


def list_all(item): 
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)
    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        title = scrapertools.find_single_match(article, '<h2 class="Title">(.*?)</h2>')
        if not url or not title: continue
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        year = scrapertools.find_single_match(article, '<span class="Year">(\d+)</span>')
        if not year: year = '-'
        plot = scrapertools.find_single_match(article, '<div class="Description">\s*<p>(.*?)</p>')

        tipo = 'tvshow' if 'Serie TV</span>' in article else 'movie'
        if item.search_type not in ['all', tipo]: continue
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            qlty_lang = scrapertools.find_single_match(article, '<span class="calidad">([^<]+)')
            if '|' in qlty_lang:
                qlty = qlty_lang.split('|')[0].strip()
                lang = qlty_lang.split('|')[1].strip()
            else:
                qlty = qlty_lang
                lang = ''
            
            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, 
                                        qualities=qlty, languages=IDIOMAS.get(lang, lang),
                                        contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot} ))
        else:
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    next_page = scrapertools.find_single_match(data, '<a class="next page-numbers" href="([^"]+)')
    if next_page:
       itemlist.append(item.clone (url = next_page, title = '>> Página siguiente', action = 'list_all'))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    
    matches = re.compile(' data-tab="(\d+)"', re.DOTALL).findall(data)
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
    itemlist = []

    data = httptools.downloadpage(item.url).data

    if item.contentSeason: # reducir datos a la temporada pedida
        data = scrapertools.find_single_match(data, ' data-tab="%s"(.*?)</table>' % item.contentSeason)

    matches = re.compile('<tr>(.*?)</tr>', re.DOTALL).findall(data)
    for data_epi in matches:
        try:
            url, title = scrapertools.find_single_match(data_epi, '<td class="MvTbTtl"><a href="([^"]+)">([^<]*)</a>')
            season, episode = scrapertools.find_single_match(url, '-(\d+)(?:x|X)(\d+)/$')
        except:
            continue
        if not url or not season or not episode: continue
        if item.contentSeason and item.contentSeason != int(season): continue

        thumb = scrapertools.find_single_match(data_epi, ' src="([^"]+)')
        if thumb.startswith('//'): thumb = 'https:' + thumb
        titulo = '%sx%s %s' % (season, episode, title)

        itemlist.append(item.clone( action='findvideos', url=url, title=titulo, thumbnail=thumb, 
                                    contentType='episode', contentSeason=season, contentEpisodeNumber=episode ))

    tmdb.set_infoLabels(itemlist)

    return itemlist



# Asignar un numérico según las calidades del canal, para poder ordenar por este valor
def puntuar_calidad(txt):
    txt = txt.replace(' ', '').replace('-', '').lower()
    orden = ['cam', 'hdcam', 'webscreener', 'tsscreener', 'brscreener', 'hdtv', 'hdtv720p', 'microhd', 'dvdrip', 'bluraymicrohd', 'blurayrip', 'hdrip', 'hd720', 'hd1080', '4kuhdmicro']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1

def normalize_server(server):
    server = servertools.corregir_servidor(server)
    return server

def findvideos(item):
    logger.info()
    itemlist = []
    
    data = httptools.downloadpage(item.url).data
    # ~ logger.debug(data)

    # Enlaces en embeds
    patron = ' data-TPlayerNv="(Opt[^"]+)"><span>Opción <strong>[^<]*</strong></span> <span>([^<]+)'
    matches = re.compile(patron, re.DOTALL | re.IGNORECASE).findall(data)
    for opt, lang_qlty in matches:
        if 'Trailer' in lang_qlty: continue
        url = scrapertools.find_single_match(data, 'id="%s">&lt;iframe.*? src=&quot;(.*?)&quot;' % opt)
        if not url: continue

        servidor = servertools.get_server_from_url(url)
        if not servidor or servidor == 'directo': continue
        url = servertools.normalize_url(servidor, url)

        l_q = scrapertools.find_single_match(lang_qlty, '(.*?)-(.*?)$')
        if l_q:
            lang = l_q[0].strip()
            qlty = l_q[1].strip()
        else:
            lang = ''
            qlty = lang_qlty

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor,
                              title = '', url = url, 
                              language = IDIOMAS.get(lang, lang), quality = qlty, quality_num = puntuar_calidad(qlty), other = 'e'
                       ))

    # Enlaces en descargas
    if '<div class="Title">Enlaces</div>' in data:
        bloque = scrapertools.find_single_match(data, '<div class="Title">Enlaces</div>(.*?)</table>')
        matches = re.compile('<tr>(.*?)</tr>', re.DOTALL).findall(bloque)
        for lin in matches:
            # ~ logger.debug(lin)
            if '<th' in lin: continue
            url = scrapertools.find_single_match(lin, ' href="([^"]+)')
            if url.startswith('//'): url = 'https:' + url
            # ~ if '/safelink/' in url: continue # descartar pq requieren 15 segundos de espera !?
            
            spans = scrapertools.find_multiple_matches(lin, '<span>(.*?)</span>')
            if len(spans) != 3: continue
            server = scrapertools.find_single_match(spans[0], '>([^.]+)').strip().lower()
            lang = scrapertools.find_single_match(spans[1], '>(.*?)$').strip()
            qlty = spans[2]

            if not url or not server: continue
            if server.lower() != 'torrent': continue # descartar lo que no sea torrent pq son servidores con debrider !?
            
            itemlist.append(Item( channel = item.channel, action = 'play', server = normalize_server(server),
                                  title = '', url = url, 
                                  language = IDIOMAS.get(lang, lang), quality = qlty, quality_num = puntuar_calidad(qlty) , other = 'd'
                           ))

    return itemlist

def play(item):
    logger.info()
    itemlist = []

    if item.url.startswith(host) and '/safelink/' in item.url:
        data = httptools.downloadpage(item.url).data
        # ~ logger.debug(data)
        
        url = scrapertools.find_single_match(data, ' action="([^"]+)')
        if not url: return itemlist
        if url.startswith('/'): url = host + url[1:]
        
        post = {}
        inputs = scrapertools.find_multiple_matches(data, '<input type="hidden" name="([^"]+)"(?: autocomplete="off"|) value="([^"]+)"')
        for nom, val in inputs:
            post[nom] = val

        espera = scrapertools.find_single_match(data, '<span id="timer" class="timer">\s*(\d+)')
        if espera:
            import time
            from platformcode import platformtools
            platformtools.dialog_notification('Cargando', 'Espera de %s segundos requerida' % espera)
            time.sleep(int(espera))

        headers = {'Referer': item.url, 'X-Requested-With': 'XMLHttpRequest'}
        data = httptools.downloadpage(url, post=post, headers=headers).data
        # ~ logger.debug(data)
        
        url = scrapertools.find_single_match(data.replace('\\/', '/'), '"url":"([^"]+)')
        if url:
            servidor = servertools.get_server_from_url(url)
            if servidor and servidor != 'directo':
                url = servertools.normalize_url(servidor, url)
                itemlist.append(item.clone( url=url, server=servidor ))

    else:
        itemlist.append(item.clone())

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '?s=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
