# -*- coding: utf-8 -*-

import re, base64

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools

host = 'https://www.pelispedia.de/'


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

    itemlist.append(item.clone ( title = 'Últimas películas', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone ( title = 'Por año', action = 'anios', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist

def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Últimas series', action = 'list_all', url = host + 'serie/', search_type = 'tvshow' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    itemlist.append(item.clone ( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    bloque = scrapertools.find_single_match(data, '<h3 class="widget-title">GENEROS</h3><ul>(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)"[^>]*>([^<]+)</a>')
    for url, title in matches:
        url += '?type=series' if item.search_type == 'tvshow' else '?type=movies'
        itemlist.append(item.clone( action='list_all', title=title, url=url ))

    return itemlist

def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1949, -1):
        itemlist.append(item.clone( title=str(x), url= host + 'release/' + str(x) + '/', action='list_all' ))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url, raise_weberror=False).data
    data = re.sub('<aside class="sidebar".*?</aside>', '', data, flags=re.DOTALL)
    # ~ logger.debug(data)

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)
    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)')
        if not url: url = scrapertools.find_single_match(article, ' href=([^ >]+)')

        title = scrapertools.find_single_match(article, '<h2 class="entry-title">(.*?)</h2>')
        if not title: title = scrapertools.find_single_match(article, '<h4>(.*?)</h4>')
        if not title: title = scrapertools.find_single_match(article, ' alt="([^"]+)"')
        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, ' src="([^"]+)')
        if not thumb: thumb = scrapertools.find_single_match(article, ' src=([^ >]+)')

        year = scrapertools.find_single_match(article, '<span class="year">(\d{4})</span>')
        if not year: year = scrapertools.find_single_match(article, '<span>(\d{4})</span>')
        if not year: year = scrapertools.find_single_match(article, ' (\d{4})</span>')
        if not year and '/release/' in item.url: year = scrapertools.find_single_match(item.url, '/release/(\d{4})')
        if not year: year = '-'

        tipo = 'tvshow' if '/serie/' in url else 'movie'
        if item.search_type not in ['all', tipo]: continue
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            qlty = scrapertools.find_single_match(article, '<span class="Qlty">([^<]+)')

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, 
                                        qualities=qlty,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))
        else:
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    next_page = scrapertools.find_single_match(data, '<a href="([^"]+)"[^>]*>SIGUIENTE</a>')
    if next_page:
       itemlist.append(item.clone (url = next_page, title = '>> Página siguiente', action = 'list_all'))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = re.compile(' href="([^"]+)"[^>]*>Temporada<dt[^>]*>(\d+)</dt>', re.DOTALL).findall(data)
    for url, numtempo in matches:
        itemlist.append(item.clone( action='episodios', title='Temporada %s' % numtempo, url=url,
                                    contentType='season', contentSeason=numtempo ))

    tmdb.set_infoLabels(itemlist)

    return itemlist

# Si una misma url devuelve los episodios de todas las temporadas, definir rutina tracking_all_episodes para acelerar el scrap en trackingtools.
# ~ def tracking_all_episodes(item):
    # ~ return episodios(item)

def episodios(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    # ~ logger.debug(data)

    bloque = scrapertools.find_single_match(data, '<ul id="episode_by_temp"[^>]*>(.*?)</ul>')

    matches = re.compile('<li(.*?)</li>', re.DOTALL).findall(bloque)
    for data_epi in matches:

        url = scrapertools.find_single_match(data_epi, ' href="([^"]+)')
        season, episode = scrapertools.find_single_match(data_epi, '<span class="num-epi">(\d+)x(\d+)')
        if not url or not season or not episode: continue

        thumb = scrapertools.find_single_match(data_epi, ' src="([^"]+)')
        title = scrapertools.find_single_match(data_epi, '<h2 class="entry-title">(.*?)</h2>')
        title = title.replace('%sx%s' % (season, episode), '').strip()
        titulo = '%sx%s %s' % (season, episode, title)

        itemlist.append(item.clone( action='findvideos', url=url, title=titulo, thumbnail=thumb, 
                                    contentType='episode', contentSeason=season, contentEpisodeNumber=episode ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


# Asignar un numérico según las calidades del canal, para poder ordenar por este valor
def puntuar_calidad(txt):
    txt = txt.replace(' ', '').replace('-', '').lower()
    orden = ['cam', 'tsscreener', 'brscreener', 'sd240p', 'sd480p', 'dvdrip', 'hd', 'hdrip', 'hd720p', 'hd1080p']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1

def corregir_servidor(servidor):
    servidor = servertools.corregir_servidor(servidor)
    if servidor == 'fcom': return 'fembed'
    elif servidor in ['mp4', 'api', 'drive']: return 'gvideo'
    elif servidor == 'streamcrypt': return ''
    elif servidor in ['stream', 'stream-mx', 'stream mx', 'streammx', 'mx server']: return 'directo'
    else: return servidor

def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'es':'Esp', 'mx':'Lat', 'en':'VOSE',  'spanish':'Esp','español':'Esp', 'latino':'Lat', 'subtitulado':'VOSE', 'inglés':'VO'}

    data = httptools.downloadpage(item.url).data
    # ~ logger.debug(data)

    # Enlaces en embeds
    matches_url = scrapertools.find_multiple_matches(data, '<div id="options-.*? data-src="([^"]+)')
    matches_info = scrapertools.find_multiple_matches(data, '<span class="server">(.*?)</span>')
    for i, url in enumerate(matches_url):
        if i >= len(matches_info): continue
        lang = scrapertools.find_single_match(matches_info[i], '-([^-]+)$').lower().strip()
        server = scrapertools.find_single_match(matches_info[i], '^([^-]+)')
        server = corregir_servidor(server)
        if not server: continue

        itemlist.append(Item( channel = item.channel, action = 'play', server = server, referer = item.url,
                              title = '', url = url, 
                              language = IDIOMAS.get(lang, lang), other = 'e'
                       ))

    # Enlaces en descargas
    bloque = scrapertools.find_single_match(data, '<div class="download-links">(.*?)</table>')
    matches = re.compile('<tr(.*?)</tr>', re.DOTALL).findall(bloque)
    for lin in matches:
        # ~ logger.debug(lin)
        if '<th' in lin: continue

        url = scrapertools.find_single_match(lin, " href=(?:'|\")([^'\"]+)")
        if not url: url = scrapertools.find_single_match(lin, " href=([^ >]+)")
        if url.startswith('//'): url = 'https:' + url
        if not url: continue
        
        tds = scrapertools.find_multiple_matches(lin, '<td>(.*?)</td>')

        server = corregir_servidor(scrapertools.find_single_match(tds[0], "</span>(.*)$"))
        if not server: continue
        lang = tds[1].lower().strip()
        qlty = scrapertools.find_single_match(tds[2], "<span>(.*)</span>")

        itemlist.append(Item( channel = item.channel, action = 'play', server = server, referer = item.url,
                              title = '', url = url, 
                              language = IDIOMAS.get(lang, lang), quality = qlty, quality_num = puntuar_calidad(qlty), other = 'd'
                       ))

    return itemlist

def play(item):
    logger.info()
    itemlist = []

    if '/o.php?l=' in item.url:
        url = scrapertools.find_single_match(item.url, "/o\.php\?l=(.*)")
        for i in range(9): # range(5)
            url = base64.b64decode(url)
            if url.startswith('http'): break
        if not url.startswith('http'): url = None
    else:
        item.url = item.url.replace('&#038;', '&')
        resp = httptools.downloadpage(item.url, headers={'Referer': item.referer}, follow_redirects=False)
        if 'location' in resp.headers: 
            url = resp.headers['location']
        else:
            # ~ logger.debug(resp.data)
            url = scrapertools.find_single_match(resp.data, "src='([^']+)")
            if not url: url = scrapertools.find_single_match(resp.data, 'src="([^"]+)')
            if not url: url = scrapertools.find_single_match(resp.data, 'src=([^ >]+)')
            if not url: url = scrapertools.find_single_match(resp.data, '"embed_url":"([^"]+)')

    if 'stream-mx.com/' in url:
        fid = scrapertools.find_single_match(url, "id=([^&]+)")
        if not fid: return itemlist
        url = 'https://stream-mx.com/player.php?id=%s&v=2&ver=si' % fid
        data = httptools.downloadpage(url, headers={'Referer': item.url}).data
        # ~ logger.debug(data)
        bloque = scrapertools.find_single_match(data, '"sources":\s*\[(.*?)\]')
        for enlace in scrapertools.find_multiple_matches(bloque, "\{(.*?)\}"):
            v_url = scrapertools.find_single_match(enlace, '"file":\s*"([^"]+)')
            if not v_url: continue
            v_type = scrapertools.find_single_match(enlace, '"type":\s*"([^"]+)')
            if v_type == 'hls':
                itemlist.append(item.clone(url = v_url, server = 'm3u8hls'))
            else:
                v_lbl = scrapertools.find_single_match(enlace, '"label":\s*"([^"]+)')
                itemlist.append([v_lbl, v_url])

    elif url:
        servidor = servertools.get_server_from_url(url)
        if servidor and servidor != 'directo':
            url = servertools.normalize_url(servidor, url)
            itemlist.append(item.clone( url=url, server=servidor ))

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
