# -*- coding: utf-8 -*-

import re, urllib

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb

host = 'https://inkapelis.me/'


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data
    # ~ data = httptools.downloadpage_proxy('inkapelis', url, post=post, headers=headers).data
    return data


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series' ))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all' ))

    return itemlist

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Últimas películas', action = 'list_all', url = host + 'pelicula/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Películas en cines', action = 'list_all', url = host + 'genero/cine/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Películas destacadas', action = 'list_all', url = host + 'genero/destacadas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'En castellano', action = 'list_all', url = host + 'idioma/castellano/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'En latino', action = 'list_all', url = host + 'idioma/latino/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'En VOSE', action = 'list_all', url = host + 'idioma/subtituladas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'En calidad HD', action = 'list_all', url = host + 'calidad/hd/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Estrenos HD', action = 'list_all', url = host + 'genero/estrenos-hd/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anyos', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist

def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Últimas series', action = 'list_all', url = host + 'serie/', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Últimas temporadas', action = 'last_seasons', url = host + 'temporada/' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []
    
    data = do_downloadpage(host + 'pelicula/')
    # ~ logger.debug(data)
    
    bloque = scrapertools.find_single_match(data, '<ul class="genres scrolling">(.*?)</ul>')
    
    # ~ matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)">([^<]+)</a>\s*<i>([^<]+)')
    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)">([^<]+)<i>([^<]+)')
    for url, title, num in matches:
        if num == '0': continue
        if '/cine/' in url or '/destacadas/' in url or '/estrenos-hd/' in url: continue # ya están en el listado principal y no son géneros
        itemlist.append(item.clone( action='list_all', title='%s (%s)' % (title, num), url=url ))

    return itemlist

def anyos(item):
    logger.info()
    itemlist = []
    
    data = do_downloadpage(host + 'pelicula/')
    
    bloque = scrapertools.find_single_match(data, '<ul class="releases scrolling">(.*?)</ul>')
    
    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)">([^<]+)')
    for url, title in matches:
        itemlist.append(item.clone( action='list_all', title=title, url=url ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []
    
    data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)
    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        if thumb.startswith('//'): thumb = 'https:' + thumb
        title = scrapertools.find_single_match(article, ' alt="([^"]+)"')
        if not url or not title: continue
        title_alt = title.split('(')[0].strip() if ' (' in title else '' # para mejorar detección en tmdb

        tipo = 'tvshow' if '/serie/' in url else 'movie'
        if tipo != item.search_type: continue

        year = scrapertools.find_single_match(article, '<span class="year">(\d+)</span>')
        if not year: year = scrapertools.find_single_match(article, '<span>(\d{4})</span>')
        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<div class="texto">(.*?)</div>'))
        
        if tipo == 'movie':
            qlty = scrapertools.find_single_match(article, '<span class="quality">([^<]+)')
            langs = []
            if '<div class="castellano">' in article: langs.append('Esp')
            if '<div class="latino">' in article: langs.append('Lat')
            if '<div class="subtitulado">' in article: langs.append('VOSE')
            
            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, languages = ', '.join(langs), 
                                        contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot}, contentTitleAlt = title_alt ))
        else:
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year, 'plot': plot}, contentTitleAlt = title_alt ))

            
    tmdb.set_infoLabels(itemlist)

    next_page_link = scrapertools.find_single_match(data, ' href="([^"]+)" ><span class="icon-chevron-right">')
    if next_page_link:
        itemlist.append(item.clone( title='>> Página siguiente', url=next_page_link, action='list_all' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    
    patron = "<span class='se-t[^']*'>(\d+)</span>"
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

    patron = "<li class='mark-\d+'>(.*?)</li>"
    matches = re.compile(patron, re.DOTALL).findall(data)

    for datos in matches:
        try:
            url, title = scrapertools.find_single_match(datos, " href='([^']+)'>([^<]+)</a>")
            season, episode = scrapertools.find_single_match(datos, "<div class='numerando'>(\d+) - (\d+)")
        except:
            continue

        if item.contentSeason and item.contentSeason != int(season):
            continue

        thumb = scrapertools.find_single_match(datos, " src='([^']+)")
        titulo = '%sx%s %s' % (season, episode, title)

        itemlist.append(item.clone( action='findvideos', title = titulo, thumbnail=thumb, url = url,
                                    contentType = 'episode', contentSeason = season, contentEpisodeNumber = episode ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def last_seasons(item):
    logger.info()
    itemlist=[]

    data = do_downloadpage(item.url)
    
    matches = re.compile(' class="item se seasons"(.*?)</article>', re.DOTALL).findall(data)
    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        title = scrapertools.find_single_match(article, '<span class="c">(.*?)</span>')
        numtempo = scrapertools.find_single_match(article, '<span class="b">(\d+)</span>')
        if not url or not title or not numtempo: continue

        itemlist.append(item.clone( action='episodios', title='%s - Temporada %s' % (title, numtempo),
                                    thumbnail=thumb, url = url,
                                    contentType='season', contentSeason=numtempo, contentSerieName=title ))
        
    tmdb.set_infoLabels(itemlist)

    next_page_link = scrapertools.find_single_match(data, ' href="([^"]+)" ><span class="icon-chevron-right">')
    if next_page_link:
        itemlist.append(item.clone( title='>> Página siguiente', url=next_page_link, action='list_all' ))

    return itemlist


def corregir_servidor(servidor):
    servidor = servertools.corregir_servidor(servidor)
    if servidor == 'drive': return 'gvideo'
    elif servidor == 'drive [vip]': return 'gvideo'
    elif servidor == 'descargar': return 'mega' # !? 1fichier
    elif servidor == 'vip': return 'directo'
    elif servidor == 'premium': return 'digiload'
    elif servidor == 'goplay': return 'gounlimited'
    elif servidor in ['meplay', 'megaplay']: return 'netutv'
    elif servidor == 'playerv': return 'directo' # storage.googleapis.com
    elif servidor == 'stream': return 'mystream'
    else: return servidor

def findvideos(item):
    logger.info()
    itemlist = []
    
    IDIOMAS = {'castellano': 'Esp', 'latino': 'Lat', 'subtitulado': 'VOSE'}

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    matches = scrapertools.find_multiple_matches(data, "<li id='player-option-\d+'(.*?)</li>")
    for enlace in matches:
        # ~ logger.debug(enlace)

        dtype = scrapertools.find_single_match(enlace, "data-type='([^']+)")
        dpost = scrapertools.find_single_match(enlace, "data-post='([^']+)")
        dnume = scrapertools.find_single_match(enlace, "data-nume='([^']+)")
        if dnume == 'trailer': continue
        if not dtype or not dpost or not dnume: continue
        
        lang = scrapertools.find_single_match(enlace, "/img/flags/([^.']+)").lower()

        post = urllib.urlencode( {'action': 'doo_player_ajax', 'post': dpost, 'nume': dnume, 'type': dtype} )
        data2 = do_downloadpage(host + 'wp-admin/admin-ajax.php', post=post, headers={'Referer':item.url})
        url = scrapertools.find_single_match(data2, "src='([^']+)")
        if not url: continue
        # ~ logger.info(url)

        # ~ src='//playerd.xyz/play.php?v=//jplayer.club/v/11g5xij6ryq2-wr'
        if 'play.php?v=' in url:
            vurl = url.split('play.php?v=')[1]
            if vurl.startswith('//'): vurl = 'https:' + vurl
            servidor = servertools.get_server_from_url(vurl)
            # ~ logger.info(servidor)
            if servidor and servidor != 'directo':
                vurl = servertools.normalize_url(servidor, vurl)
                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor,
                                      title = '', url = vurl,
                                      language = IDIOMAS.get(lang, 'VO')
                               ))

        # ~ https://embed.playerd.xyz/players/...
        # ~ https://players.inkapelis.me/players/
        # ~ https://is.playerd.xyz/embed/...
        # ~ https://pbgzqk.inkapelis.me/embed/...
        else:
            data2 = httptools.downloadpage(url, headers={'Referer':host}).data
            # ~ logger.debug(data2)
            
            links = scrapertools.find_multiple_matches(data2, '<a id="servers"(.*?)</a>')
            for lnk in links:
                lembed = scrapertools.find_single_match(lnk, 'data-embed="([^"]+)')
                ltype = scrapertools.find_single_match(lnk, 'data-type="([^"]+)')
                servidor = scrapertools.find_single_match(lnk, 'title="([^".]+)').lower()
                # ~ logger.info(servidor)
            
                itemlist.append(Item( channel = item.channel, action = 'play', server = corregir_servidor(servidor), referer = url,
                                      title = '', lembed = lembed, ltype = ltype, lurl = '/'.join(url.split('/')[:3]), #other=servidor,
                                      language = IDIOMAS.get(lang, 'VO')
                               ))
            if not links:
                dom = '/'.join(url.split('/')[:3])
                links = get_sources(data2)
                for lnk in links:
                    if lnk[0].startswith('/'): lnk[0] = dom + lnk[0]
                    itemlist.append(Item( channel = item.channel, action = 'play', server = '', # directo !?
                                          title = '', url = lnk[0], referer = url,
                                          language = IDIOMAS.get(lang, 'VO')
                                   ))

    return itemlist

def play(item):
    logger.info()
    itemlist = []

    if item.lembed and item.ltype and item.lurl:
        post = urllib.urlencode( {'type': item.ltype, 'streaming': item.lembed} )
        data = httptools.downloadpage(item.lurl + '/edge-data/', post=post, headers={'Referer':item.referer}).data
        # ~ logger.debug(data)

        item.url = scrapertools.find_single_match(data, '"url": "([^"]+)')
        if not item.url:
            if data.startswith('http'): item.url = data
            elif data.startswith('/'): item.url = item.lurl + data
        if not item.url: return itemlist

    if 'playerd.xyz/' in item.url or 'inkapelis.me/' in item.url:
        resp = httptools.downloadpage(item.url, headers={'Referer':item.referer}, follow_redirects=False)
        
        if 'refresh' in resp.headers:
            vurl = scrapertools.find_single_match(resp.headers['refresh'], ';\s*(.*)')
        elif 'location' in resp.headers:
            vurl = resp.headers['location']
        else:
            # ~ logger.debug(resp.data)
            url = scrapertools.find_single_match(resp.data, '<iframe src="([^"]+)')
            if not url: url = scrapertools.find_single_match(resp.data, "window\.open\('([^']+)")
            if url and url.startswith('/'): url = '/'.join(item.url.split('/')[:3]) + url

            if 'playerd.xyz/' in url or 'inkapelis.me/' in url:
                url = url.replace('iframe?url=', 'redirect?url=')
                resp = httptools.downloadpage(url, headers={'Referer':item.url}, follow_redirects=False)

                if 'refresh' in resp.headers:
                    vurl = scrapertools.find_single_match(resp.headers['refresh'], ';\s*(.*)')
                elif 'location' in resp.headers:
                    vurl = resp.headers['location']
                else:
                    # ~ logger.debug(resp.data)
                    vurl = scrapertools.find_single_match(resp.data, 'downloadurl = "([^"]+)')

            else:
                if url: 
                    vurl = url
                else: 
                    gk_link = scrapertools.find_single_match(resp.data, 'config_player\.link = "([^"]+)')
                    if gk_link:
                        post = 'link=' + gk_link
                        data = httptools.downloadpage('https://players.inkapelis.me/player/plugins/gkpluginsphp.php', post=post).data
                        # ~ logger.debug(data)
                        vurl = scrapertools.find_single_match(data, '"link":"([^"]+)').replace('\\/', '/')
                    else:
                        vurl = None
                        dom = '/'.join(item.url.split('/')[:3])
                        links = get_sources(resp.data)
                        for lnk in links:
                            if lnk[0].startswith('/'): lnk[0] = dom + lnk[0]
                            if lnk[1] == 'hls':
                                itemlist.append(item.clone(url = lnk[0], server = 'm3u8hls'))
                            else:
                                itemlist.append([lnk[2], lnk[0]])

    elif item.url.startswith('http'):
        vurl = item.url


    if vurl and 'player.php?id=' in vurl:
        resp = httptools.downloadpage(vurl, headers={'Referer':item.url}, follow_redirects=False)
        # ~ logger.debug(resp.data)
        dom = '/'.join(vurl.split('/')[:3])
        links = get_sources(resp.data)
        for lnk in links:
            if lnk[0].startswith('/'): lnk[0] = dom + lnk[0]
            if lnk[1] == 'hls':
                itemlist.append(item.clone(url = lnk[0], server = 'm3u8hls'))
            else:
                itemlist.append([lnk[2], lnk[0]])
        vurl = None

    if vurl:
        # ~ logger.info(vurl)
        servidor = servertools.get_server_from_url(vurl)
        if servidor and (servidor != 'directo' or 'googleapis.com' in vurl):
            url = servertools.normalize_url(servidor, vurl)
            itemlist.append(item.clone( url=url, server=servidor ))

    return itemlist

def get_sources(data):
    srcs = []
    bloque = scrapertools.find_single_match(data, '(?:"|)sources(?:"|):\s*\[(.*?)\]')
    for enlace in scrapertools.find_multiple_matches(bloque, "\{(.*?)\}"):
        v_url = scrapertools.find_single_match(enlace, '(?:"|)file(?:"|):\s*"([^"]+)')
        if not v_url: continue
        v_type = scrapertools.find_single_match(enlace, '(?:"|)type(?:"|):\s*"([^"]+)')
        v_lbl = scrapertools.find_single_match(enlace, '(?:"|)label(?:"|):\s*"([^"]+)')
        if not v_lbl: v_lbl = 'mp4'
        srcs.append([v_url, v_type, v_lbl])

    return srcs



def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    matches = re.compile('<div class="result-item">(.*?)</article>', re.DOTALL).findall(data)
    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        title = scrapertools.find_single_match(article, ' alt="([^"]+)"')
        if not url or not title: continue
        title_alt = title.split('(')[0].strip() if ' (' in title else '' # para mejorar detección en tmdb

        tipo = 'tvshow' if '/serie/' in url else 'movie'
        if item.search_type not in ['all', tipo]: continue
        sufijo = '' if item.search_type != 'all' else tipo

        year = scrapertools.find_single_match(article, '<span class="year">(\d+)</span>')
        if not year: year = scrapertools.find_single_match(article, '<span>(\d{4})</span>')
        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<p>(.*?)</p>'))
        
        if tipo == 'movie':
            langs = []
            if 'castellano.png' in article: langs.append('Esp')
            if 'latino.png' in article: langs.append('Lat')
            if 'subtitulado.png' in article: langs.append('VOSE')

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, languages = ', '.join(langs), 
                                        contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot}, contentTitleAlt = title_alt ))
        else:
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year, 'plot': plot}, contentTitleAlt = title_alt ))

            
    tmdb.set_infoLabels(itemlist)

    next_page_link = scrapertools.find_single_match(data, ' href="([^"]+)" ><span class="icon-chevron-right">')
    if next_page_link:
        itemlist.append(item.clone( title='>> Página siguiente', url=next_page_link, action='list_search' ))

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
