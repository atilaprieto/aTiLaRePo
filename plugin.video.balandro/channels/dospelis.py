# -*- coding: utf-8 -*-

import re, urllib

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools

host = 'https://www.dospelis.online/'

perpage = 15 # preferiblemente un múltiplo de los elementos que salen en la web (5x9=45) para que la subpaginación interna no se descompense


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
    
    itemlist.append(item.clone( title = 'Últimas películas', action = 'list_all', url = host + 'movies/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'genre/estrenos/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Destacadas', action = 'list_all', url = host + 'genre/destacadas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = host + 'genre/castellano/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = host + 'genre/latino/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por productora', action = 'productoras', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []
    
    itemlist.append(item.clone( title = 'Últimas series', action = 'list_all', url = host + 'tvshows/', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Últimos episodios', action = 'list_episodes', url = host + 'episodes/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    return itemlist


def productoras(item):
    logger.info()
    itemlist = []

    opciones = [
        ('dc','DC'), 
        ('disney','Disney'), 
        ('dreamworks-animation','Dreamworks'), 
        ('marvel','Marvel'), 
        # ~ ('netflix','Netflix'), 
        ('youtube-peliculas','Youtube'), 
    ]
    for opc, tit in opciones:
        itemlist.append(item.clone( title=tit, url=host + 'genre/' + opc + '/', action='list_all' ))

    return itemlist

def generos(item):
    logger.info()
    itemlist = []
    
    descartes = ['estrenos', 'destacadas', 'castellano', 'latino', 'proximos-estrenos', 
                 'dc','disney','dreamworks-animation','marvel','netflix','youtube-peliculas']

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    data = httptools.downloadpage(host).data
    data = scrapertools.find_single_match(data, '<nav class="genres">(.*?)</nav>')

    matches = re.compile('<li class="cat-item[^"]*"><a href="([^"]+)"(?: title="[^"]*"|)>([^<]+)</a>\s*<i>([^<]+)</i>', re.DOTALL).findall(data)
    for url, title, cantidad in matches:
        if cantidad == '0': continue
        if descartar_xxx and scrapertools.es_genero_xxx(title): continue

        # Descartar los que ya están en el menú principal
        descartar = False
        for x in descartes:
            if url.endswith('/'+x+'/'):
                descartar = True
                break
        if descartar: continue

        # ~ titulo = '%s (%s)' % (title.strip().capitalize(), cantidad)
        titulo = title.strip().capitalize()
        itemlist.append(item.clone( title=titulo, url=url, action='list_all' ))

    return sorted(itemlist, key=lambda it: it.title)

def anios(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data
    data = scrapertools.find_single_match(data, '<nav class="releases">(.*?)</nav>')

    matches = re.compile('<li><a href="([^"]+)">([0-9–]+)</a>', re.DOTALL).findall(data)
    for url, title in matches:
        itemlist.append(item.clone( title=title, url=url, action='list_all' ))

    return itemlist



def list_episodes(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data
    # ~ logger.debug(data)

    matches = re.compile('<article (.*?)</article>', re.DOTALL).findall(data)
    num_matches = len(matches)

    for article in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        show = scrapertools.find_single_match(article, '<span class="serie">([^<]+)</span>')
        quality = scrapertools.find_single_match(article, '<span class="quality">([^<]+)</span>')
        title = scrapertools.find_single_match(article, '<h3><a[^>]+>([^<]+)</a></h3>')

        s_e = scrapertools.find_single_match(url, '-(\d+)x(\d+)/$')
        if not s_e: continue
        titulo = '%sx%s %s - %s' % (s_e[0], s_e[1], show, title)

        itemlist.append(item.clone( action='findvideos', title = titulo, url = url, thumbnail=thumb,
                                    contentType = 'episode', contentSerieName=show, contentSeason = s_e[0], contentEpisodeNumber = s_e[1] ))

    tmdb.set_infoLabels(itemlist)

    # Subpaginación interna y/o paginación de la web
    buscar_next = True
    if num_matches > perpage: # subpaginación interna dentro de la página si hay demasiados items
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title='>> Página siguiente', page=item.page + 1, action='list_episodes' ))
            buscar_next = False

    if buscar_next:
        next_page_link = scrapertools.find_single_match(data, '<a class=\'arrow_pag\' href="([^"]+)')
        if next_page_link:
            itemlist.append(item.clone( title='>> Página siguiente', url=next_page_link, page=0, action='list_episodes' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data
    # ~ logger.debug(data)

    matches = re.compile('<article (.*?)</article>', re.DOTALL).findall(data)
    
    matches = filter(lambda x: not 'post-featured-' in x, matches) # descartar lista de destacadas
    
    if item.search_type != 'all': # eliminar pelis/series según corresponda
        matches = filter(lambda x: ('class="item movies"' in x and item.search_type == 'movie') or \
                                   ('class="item tvshows"' in x and item.search_type == 'tvshow'), matches)
    num_matches = len(matches)

    for article in matches[item.page * perpage:]:
        tipo = scrapertools.find_single_match(article, 'class="item (\w+)s"')
        if tipo not in ['movie', 'tvshow']: continue
        sufijo = '' if item.search_type != 'all' else tipo

        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        title = scrapertools.find_single_match(article, '<h4>([^<]+)</h4>')
        year = scrapertools.find_single_match(article, '<span>([0-9]{4})</span>')
        quality = scrapertools.find_single_match(article, '<span class="quality">([^<]+)</span>')
        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<div class="texto">(.*?)</div>'))

        if tipo == 'movie':
            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                        qualities=quality, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot} ))
        else:
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, 
                                        qualities=quality, fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year, 'plot': plot} ))

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
        next_page_link = scrapertools.find_single_match(data, '<a class=\'arrow_pag\' href="([^"]+)')
        if next_page_link:
            itemlist.append(item.clone( title='>> Página siguiente', url=next_page_link, page=0, action='list_all' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    # ~ logger.debug(data)

    matches = re.compile("<span class='title'>Temporada (\d+)", re.DOTALL).findall(data)
    for numtempo in matches:
        itemlist.append(item.clone( action='episodios', title='Temporada %s' % numtempo,
                                    contentType='season', contentSeason=numtempo ))
        
    tmdb.set_infoLabels(itemlist)

    return sorted(itemlist, key=lambda it: it.title)


# Si una misma url devuelve los episodios de todas las temporadas, definir rutina tracking_all_episodes para acelerar el scrap en trackingtools.
def tracking_all_episodes(item):
    return episodios(item)


def episodios(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    # ~ logger.debug(data)
    
    if item.contentSeason: # reducir datos a la temporada pedida
        data = scrapertools.find_single_match(data, "<span class='se-t[^']*'>%d</span>(.*?)</ul>" % item.contentSeason)

    patron = "<li[^>]*><div class='imagen'><img src='([^']+)'></div><div class='numerando'>([^<]+)</div><div class='episodiotitle'><a href='([^']+)'>([^<]+)"
    matches = re.compile(patron, re.DOTALL).findall(data)

    for thumb, s_e, url, title in matches:
        try:
            season, episode = scrapertools.find_single_match(s_e, '(\d+)\s*(?:-|x|X)\s*(\d+)')
        except:
            continue

        titulo = '%sx%s %s' % (season, episode, title)
        itemlist.append(item.clone( action='findvideos', url=url, title=titulo,
                                    contentType='episode', contentSeason=season, contentEpisodeNumber=episode ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def corregir_servidor(servidor):
    servidor = servertools.corregir_servidor(servidor)
    if servidor == 'fcom': return 'fembed'
    elif servidor in ['mp4', 'api', 'drive']: return 'gvideo'
    elif servidor == 'streamcrypt': return ''
    else: return servidor


# Asignar un numérico según las calidades del canal, para poder ordenar por este valor
def puntuar_calidad(txt):
    txt = txt.lower().replace(' ', '').replace('-', '')
    orden = ['cam', 'tsscreener', 'dvdscreener', 'brscreener', 'dvdrip', 'hd', 'hd720p', 'hd1080p']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1

def findvideos(item):
    logger.info()
    itemlist = []
    
    IDIOMAS = {'es':'Esp', 'mx':'Lat', 'en':'VOSE', 'castellano':'Esp', 'latino':'Lat', 'subtitulado':'VOSE'}

    data = httptools.downloadpage(item.url).data
    # ~ logger.debug(data)

    # Fuentes de vídeo
    bloque = scrapertools.find_single_match(data, "<ul id='playeroptionsul'>(.*?)</ul>")

    matches = scrapertools.find_multiple_matches(bloque, "<li id='player-option-\d+'(.*?)</li>")
    for enlace in matches:
        # ~ logger.debug(enlace)

        dtype = scrapertools.find_single_match(enlace, "data-type='([^']+)")
        dpost = scrapertools.find_single_match(enlace, "data-post='([^']+)")
        dnume = scrapertools.find_single_match(enlace, "data-nume='([^']+)")
        if dnume == 'trailer': continue
        servidor = corregir_servidor(scrapertools.find_single_match(enlace, "<span class='server'>([^<.]+)"))
        if not dtype or not dpost or not dnume: continue
        lang = scrapertools.find_single_match(enlace, "/img/flags/([^.']+)").lower()

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor,
                              title = '', dtype = dtype, dpost = dpost, dnume = dnume, referer = item.url,
                              language = IDIOMAS.get(lang, lang)
                       ))

    # Ver en línea
    bloque = scrapertools.find_single_match(data, "<div id='videos'(.*?)</table></div></div></div>")

    matches = scrapertools.find_multiple_matches(bloque, "<tr id='link-[^']+'>(.*?)</tr>")
    for enlace in matches:
        # ~ logger.debug(enlace)

        url = scrapertools.find_single_match(enlace, " href='([^']+)")
        servidor = corregir_servidor(scrapertools.find_single_match(enlace, "domain='([^'.]+)"))
        if not url or not servidor: continue
        uploader = scrapertools.find_single_match(enlace, "author/[^/]+/'>([^<]+)</a>")
        tds = scrapertools.find_multiple_matches(enlace, '<td>(.*?)</td>')
        quality = scrapertools.find_single_match(tds[1], "<strong class='quality'>([^<]+)")
        lang = tds[2].lower()
        
        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, 
                              title = '', url = url,
                              language = IDIOMAS.get(lang,lang), quality = quality, quality_num = puntuar_calidad(quality), other = uploader
                       ))

    # Descarga ?
    # ~ bloque = scrapertools.find_single_match(data, "<div id='download'(.*?)</table></div></div></div>")

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if item.url:
        data = do_downloadpage(item.url)
        # ~ logger.debug(data)
        url = scrapertools.find_single_match(data, '<a id="link" href="([^"]+)')
        if url: 
            itemlist.append(item.clone( url=servertools.normalize_url(item.server, url) ))

    else:
        post = urllib.urlencode( {'action': 'doo_player_ajax', 'post': item.dpost, 'nume': item.dnume, 'type': item.dtype} )
        data = httptools.downloadpage(host + 'wp-admin/admin-ajax.php', post=post, headers={'Referer':item.referer}).data
        # ~ logger.debug(data)
        url = scrapertools.find_single_match(data, "src='([^']+)")
        if not url: url = scrapertools.find_single_match(data, 'src="([^"]+)')
        if url: 
            if 'jwplayer' in url and 'source=' in url: # Ej: https://www.dospelis.online/jwplayer-2/?source=https%3A%2F%2Fyoutu.be%2Fzcn89lxhEWk&id=71977&type=mp4
                url = urllib.unquote(scrapertools.find_single_match(url, "source=([^&']+)"))
            elif 'streamcrypt.net/' in url: # Ej: https://streamcrypt.net/embed/streamz.cc/...
                url = scrapertools.decode_streamcrypt(url)

            if not url: return itemlist
            servidor = servertools.get_server_from_url(url)
            if servidor and servidor != 'directo':
                url = servertools.normalize_url(servidor, url)
                itemlist.append(item.clone( url=url, server=servidor ))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data
    # ~ logger.debug(data)

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)
    
    if item.search_type != 'all': # eliminar pelis/series según corresponda
        matches = filter(lambda x: ('class="movies"' in x and item.search_type == 'movie') or \
                                   ('class="tvshows"' in x and item.search_type == 'tvshow'), matches)
    num_matches = len(matches)

    for article in matches[item.page * perpage:]:
        tipo = 'tvshow' if 'class="tvshows"' in article else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        title = scrapertools.find_single_match(article, ' alt="([^"]+)"').strip()
        year = scrapertools.find_single_match(article, '<span class="year">([0-9]{4})</span>')
        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<p>(.*?)</p>'))

        if tipo == 'movie':
            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                        fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot} ))
        else:
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, 
                                        fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year, 'plot': plot} ))

        if len(itemlist) >= perpage: break


    tmdb.set_infoLabels(itemlist)

    # Subpaginación interna y/o paginación de la web
    buscar_next = True
    if num_matches > perpage: # subpaginación interna dentro de la página si hay demasiados items
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title='>> Página siguiente', page=item.page + 1, action='list_search' ))
            buscar_next = False

    if buscar_next:
        next_page_link = scrapertools.find_single_match(data, '<a class=\'arrow_pag\' href="([^"]+)')
        if next_page_link:
            itemlist.append(item.clone( title='>> Página siguiente', url=next_page_link, page=0, action='list_search' ))

    return itemlist

def search(item, texto):
    logger.info()
    try:
        item.url = host + '?s=' + texto.replace(" ", "+")
        return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
