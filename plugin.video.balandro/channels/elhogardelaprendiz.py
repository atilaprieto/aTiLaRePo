# -*- coding: utf-8 -*-

import re

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools

host = 'https://elhogardelaprendiz.es/'


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

    itemlist.append(item.clone ( title = 'Últimas películas', action = 'list_all', url = host + 'peliculas', search_type = 'movie' ))
    itemlist.append(item.clone ( title = 'Más vistas', action = 'list_all', url = host + 'top-2/mas-vistas/', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone ( title = 'Por año', action = 'anios', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Últimas series', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))
    itemlist.append(item.clone ( title = 'Más vistas', action = 'list_all', url = host + 'top-2/mas-vistas/', search_type = 'tvshow' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone ( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    itemlist.append(item.clone ( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    return itemlist



def generos(item):
    logger.info()
    itemlist = []
    url_extra = '?tr_post_type=2' if item.search_type == 'tvshow' else '?tr_post_type=1'
    
    data = httptools.downloadpage(host).data
    
    bloque = scrapertools.find_single_match(data, 'Categorias</a><ul class="sub-menu">(.*?)</ul>')
    
    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)">([^<]+)')
    for url, title in matches:
        itemlist.append(item.clone( action='list_all', title=title, url=url + url_extra ))

    itemlist.append(item.clone ( action = 'list_all', title = 'Documental', url = host + 'documental/' + url_extra ))
    itemlist.append(item.clone ( action = 'list_all', title = 'Western', url = host + 'western/' + url_extra ))

    return sorted(itemlist, key=lambda it: it.title)

def anios(item):
    logger.info()
    itemlist = []
    url_extra = '?tr_post_type=2' if item.search_type == 'tvshow' else '?tr_post_type=1'
    url_extra += '&s=trfilter&trfilter=1&years[]='

    from datetime import datetime
    current_year = int(datetime.today().year)
    first_year = 1960 if item.search_type == 'tvshow' else 1938

    for x in range(current_year, first_year, -1):
        itemlist.append(item.clone( title=str(x), url= host + url_extra + str(x), action='list_all' ))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)
    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        title = scrapertools.find_single_match(article, '<h3 class="Title">(.*?)</h3>')
        if not url or not title: continue
        thumb = scrapertools.find_single_match(article, ' data-src="([^"]+)"')
        year = scrapertools.find_single_match(article, '<span class="Year">(\d+)</span>')
        if not year: year = '-'

        tipo = 'tvshow' if '/serie/' in url else 'movie'
        if item.search_type not in ['all', tipo]: continue
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            qlty = scrapertools.find_single_match(article, '<span class="Qlty">([^<]+)')
            
            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, fmt_sufijo=sufijo, 
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))
        else:
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

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
            url, title = scrapertools.find_single_match(data_epi, '<a href="([^"]+)">([^<]*)</a>')
            season, episode = scrapertools.find_single_match(url, '-(\d+)(?:x|X)(\d+)/$')
        except:
            continue
        if not url or not season or not episode: continue
        if item.contentSeason and item.contentSeason != int(season): continue

        thumb = scrapertools.find_single_match(data_epi.replace('&quot;','"'), ' src="([^"]+)')
        titulo = '%sx%s %s' % (season, episode, title)

        itemlist.append(item.clone( action='findvideos', url=url, title=titulo, thumbnail=thumb, 
                                    contentType='episode', contentSeason=season, contentEpisodeNumber=episode ))

    tmdb.set_infoLabels(itemlist)

    return itemlist



# Asignar un numérico según las calidades del canal, para poder ordenar por este valor
def puntuar_calidad(txt):
    txt = txt.replace(' ', '').replace('-', '').lower()
    orden = ['cam', 'tsscreener', 'brscreener', 'dvdrip', 'hdrip', 'hd720', 'hd1080']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1

def normalize_server(server):
    server = servertools.corregir_servidor(server)
    if server == 'embed': server = 'mystream'
    elif 'opción' in server: server = ''
    return server

def findvideos(item):
    logger.info()
    itemlist = []
    
    IDIOMAS = {'español': 'Esp', 'latino': 'Lat', 'subespañol': 'VOSE', 'sub': 'VO'}

    data = httptools.downloadpage(item.url).data
    # ~ logger.debug(data)

    # Enlaces en embeds
    trid_trtype = scrapertools.find_single_match(data, '(trid=[^"]+)')
    if trid_trtype:
        patron = ' data-tplayernv="([^"]+)"><span>(.*?)</span><span>(.*?)</span></li>'
        matches = re.compile(patron, re.DOTALL).findall(data)
        for opt, server, lang_qlty in matches:
            trembed = scrapertools.find_single_match(data, 'id="%s".*?trembed=([^&"]+)' % opt)
            if not trembed: continue
            url = host + '?trembed=' + trembed + '&' + trid_trtype
            l_q = scrapertools.find_single_match(lang_qlty, '(.*?)-(.*?)$')
            if l_q:
                lang = l_q[0].strip().lower()
                qlty = l_q[1].strip()
                othr = ''
            else:
                lang = ''
                qlty = ''
                othr = lang_qlty

            itemlist.append(Item( channel = item.channel, action = 'play', server = normalize_server(server),
                                  title = '', url = url, 
                                  language = IDIOMAS.get(lang, lang), quality = qlty, quality_num = puntuar_calidad(qlty), other = othr
                           ))

    # Enlaces en descargas
    if '<div class="TPTblCn">' in data:
        bloque = scrapertools.find_single_match(data, '<div class="TPTblCn">(.*?)</table>')
        bloque = scrapertools.decodeHtmlentities(bloque)
        matches = re.compile('<tr>(.*?)</tr>', re.DOTALL).findall(bloque)
        for lin in matches:
            if '<th' in lin: continue
            url = scrapertools.find_single_match(lin, ' href="([^"]+)')
            server = scrapertools.find_single_match(lin, ' alt="Descargar ([^"]+)').strip().lower()
            lang = scrapertools.find_single_match(lin, ' alt="Imagen ([^"]+)').strip().lower()
            qlty = scrapertools.find_multiple_matches(lin, '<span>(.*?)</span>')[-1].strip()
            if not url or not server: continue
            
            itemlist.append(Item( channel = item.channel, action = 'play', server = normalize_server(server),
                                  title = '', url = url, 
                                  language = IDIOMAS.get(lang, lang), quality = qlty, quality_num = puntuar_calidad(qlty) #, other = 'download'
                           ))

    return itemlist

def play(item):
    logger.info()
    itemlist = []
    
    if 'trdownload=' in item.url:
        url = httptools.downloadpage(item.url, follow_redirects=False, only_headers=True).headers.get('location', '')
    else:
        data = httptools.downloadpage(item.url).data
        # ~ logger.debug(data)
        url = scrapertools.find_single_match(data, '<iframe.*? src="([^"]+)')

    if url:
        if url.startswith('//'): url = 'https:' + url
        url = url.replace('https://uptostream/', 'https://uptostream.com/') # corregir url errónea en algunos links

        servidor = servertools.get_server_from_url(url)
        if servidor and servidor != 'directo':
            url = servertools.normalize_url(servidor, url)
            itemlist.append(item.clone( url=url, server=servidor ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        url_extra = '&tr_post_type=2' if item.search_type == 'tvshow' else '&tr_post_type=1' if item.search_type == 'movie' else ''
        item.url = host + '?s=' + texto.replace(" ", "+") + url_extra
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
