# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] < 3:
    import urllib
else:
    import urllib.parse as urllib


import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools

host = 'https://www.dospelis.online/'

perpage = 15


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    if '/release/' in url: raise_weberror = False

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'movies/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'genre/estrenos/', search_type = 'movie' ))

    # ~ itemlist.append(item.clone( title = 'Destacadas', action = 'list_all', url = host + 'genre/destacadas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'tendencias/?get=movies', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'calificaciones/?get=movies', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por productora', action = 'productoras', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'tvshows/', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Últimos episodios', action = 'list_episodes', url = host + 'episodes/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'tendencias/?get=tv', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'calificaciones/?get=tv', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = host + 'genre/castellano/' ))
    itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = host + 'genre/latino/' ))

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
        ('youtube-peliculas','Youtube')
        ]

    for opc, tit in opciones:
        itemlist.append(item.clone( title=tit, url=host + 'genre/' + opc + '/', action='list_all' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    genres = [
       ['Acción', 'accion'],
       ['Action & adventure', 'action-adventure'],
       ['Adolescencia', 'adolescencia'],
       ['Air bud', 'air-bud'],
       ['Animación', 'animacion'],
       ['Anime', 'anime'],
       ['Aventura', 'aventura'],
       ['Aventura espacial', 'aventura-espacial'],
       ['Biografía', 'biografia'],
       ['Boxeo', 'boxeo'],
       ['Bélica', 'belica'],
       ['Ciencia ficción', 'ciencia-ficcion'],
       ['Cine mudo', 'cine-mudo'],
       ['Coches', 'coches'],
       ['Comedia', 'comedia'],
       ['Crimen', 'crimen'],
       ['Deporte', 'deporte'],
       ['Documental', 'documental'],
       ['Drama', 'drama'],
       ['Drogas', 'drogas'],
       ['Enfermedad', 'enfermedad'],
       ['Eroticas +18', 'peliculas-eroticas'],
       ['Familia', 'familia'],
       ['Fantasía', 'fantasia'],
       ['Foreign', 'foreign'],
       ['Guerra', 'guerra'],
       ['Historia', 'historia'],
       ['Homosexualidad', 'homosexualidad'],
       ['Kids', 'kids'],
       ['Medicina', 'medicina'],
       ['Misterio', 'misterio'],
       ['Musical', 'musical'],
       ['Música', 'musica'],
       ['News', 'news'],
       ['Peliculas clasicas', 'peliculas-clasicas'],
       ['Peliculas trilogia y sagas', 'peliculas-trilogia-y-sagas'],
       ['Película de la televisión', 'pelicula-de-la-television'],
       ['Película de tv', 'pelicula-de-tv'],
       ['Política', 'politica'],
       ['Reality', 'reality'],
       ['Romance', 'romance'],
       ['Sci-fi & fantasy', 'sci-fi-fantasy'],
       ['Soap', 'soap'],
       ['Superhéroes', 'superheroes'],
       ['Suspense', 'suspense'],
       ['Terror', 'terror'],
       ['Thriller', 'thriller'],
       ['Transexualidad', 'transexualidad'],
       ['War & politics', 'war-politics'],
       ['Western', 'western']
       ]

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    for x in genres:
        title = x[0]

        if descartar_xxx:
            if title == 'Eroticas +18': continue

        url = host + 'genre/' + str(x[1])

        itemlist.append(item.clone( title = title, url = url, action = 'list_all' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1926, -1):
        url = host + 'release/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all' ))

    return itemlist


def list_episodes(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
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
    if num_matches > perpage:
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title='>> Página siguiente', page=item.page + 1, action='list_episodes', text_color='coral' ))
            buscar_next = False

    if buscar_next:
        next_page_link = scrapertools.find_single_match(data, '<a class=\'arrow_pag\' href="([^"]+)')
        if next_page_link:
            itemlist.append(item.clone( title='>> Página siguiente', url=next_page_link, page=0, action='list_episodes', text_color='coral' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    matches = re.compile('<article (.*?)</article>', re.DOTALL).findall(data)

    matches = list(filter(lambda x: not 'post-featured-' in x, matches)) # descartar lista de destacadas

    if item.search_type != 'all': # eliminar pelis/series según corresponda
        matches = list(filter(lambda x: ('class="item movies"' in x and item.search_type == 'movie') or \
                                   ('class="item tvshows"' in x and item.search_type == 'tvshow'), matches))
    num_matches = len(matches)

    for article in matches[item.page * perpage:]:
        tipo = scrapertools.find_single_match(article, 'class="item (\w+)s"')
        if tipo not in ['movie', 'tvshow']: continue
        sufijo = '' if item.search_type != 'all' else tipo

        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')

        title = scrapertools.find_single_match(article, '<h4>([^<]+)</h4>')
        if not title: title = scrapertools.find_single_match(article, 'alt="([^"]+)')

        year = scrapertools.find_single_match(article, '<span>(\d{4})</span>')
        if not year: year = scrapertools.find_single_match(article, '<span>.*?,\s*(\d{4})</span>').strip()
        if year: title = re.sub(' %s$' % year, '', title)

        quality = scrapertools.find_single_match(article, '<span class="quality">([^<]+)</span>')
        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<div class="texto">(.*?)</div>'))

        if tipo == 'movie':
            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=quality, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot} ))
        else:
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, qualities=quality, fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year, 'plot': plot} ))

        if len(itemlist) >= perpage: break


    tmdb.set_infoLabels(itemlist)

    # Subpaginación interna y/o paginación de la web
    buscar_next = True
    if num_matches > perpage:
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title='>> Página siguiente', page=item.page + 1, action='list_all', text_color='coral' ))
            buscar_next = False

    if buscar_next:
        next_page_link = scrapertools.find_single_match(data, '<a class=\'arrow_pag\' href="([^"]+)')
        if next_page_link:
            itemlist.append(item.clone( title='>> Página siguiente', url=next_page_link, page=0, action='list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    matches = re.compile("<span class='title'>Temporada (\d+)", re.DOTALL).findall(data)

    for numtempo in matches:
        title = 'Temporada ' + numtempo

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&'), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = numtempo, page = 0 ))

    tmdb.set_infoLabels(itemlist)

    return sorted(itemlist, key=lambda it: it.title)


# Si una misma url devuelve los episodios de todas las temporadas, definir rutina tracking_all_episodes para acelerar el scrap en trackingtools.
def tracking_all_episodes(item):
    return episodios(item)


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    perpage = 50

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    if item.contentSeason: # reducir datos a la temporada pedida
        data = scrapertools.find_single_match(data, "<span class='se-t[^']*'>" + str(item.contentSeason) + "</span>(.*?)</ul>")

    patron = "<li[^>]*><div class='imagen'><img src='([^']+)'></div><div class='numerando'>([^<]+)</div><div class='episodiotitle'><a href='([^']+)'>([^<]+)"
    matches = re.compile(patron, re.DOTALL).findall(data)

    for thumb, s_e, url, title in matches[item.page * perpage:]:
        try:
            season, episode = scrapertools.find_single_match(s_e, '(\d+)\s*(?:-|x|X)\s*(\d+)')
        except:
            continue

        titulo = '%sx%s %s' % (season, episode, title)
        itemlist.append(item.clone( action='findvideos', url=url, title=titulo, contentType='episode', contentSeason=season, contentEpisodeNumber=episode ))

        if len(itemlist) >= perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if len(matches) > (item.page + 1) * perpage:
        itemlist.append(item.clone( title=">> Página siguiente", action="episodios", page=item.page + 1, text_color='coral' ))

    return itemlist


def corregir_servidor(servidor):
    servidor = servertools.corregir_servidor(servidor)
    if servidor == 'fcom': return 'fembed'
    elif servidor in ['mp4', 'api', 'drive']: return 'gvideo'
    elif servidor == ['streamcrypt', 'desconocido']: return ''
    else: return servidor


# Asignar un numérico según las calidades del canal, para poder ordenar por este valor
def puntuar_calidad(txt):
    txt = txt.lower().replace(' ', '').replace('-', '')
    orden = ['cam', 'tsscreener', 'dvdscreener', 'brscreener', 'dvdrip', 'hd', 'hdrip', '720p', 'hd720p', '1080p', 'hd1080p']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'es': 'Esp', 'mx': 'Lat', 'en': 'Vose', 'castellano': 'Esp', 'latino': 'Lat', 'subtitulado': 'Vose'}

    data = do_downloadpage(item.url)

    # Fuentes de vídeo
    bloque = scrapertools.find_single_match(data, "<ul id='playeroptionsul'[^>]*>(.*?)</ul>")

    matches = scrapertools.find_multiple_matches(bloque, "<li id='player-option-(\d+)'(.*?)</li>")
    for numero, enlace in matches:
        # ~ logger.debug(enlace)
        # ~ <div id='source-player-1' class='source-box'><div class='pframe'><iframe class='metaframe rptss' src='https://upstream.to/embed-m63t64z83gfn.html'
        url = scrapertools.find_single_match(data, "<div id='source-player-%s[^>]*><div class='pframe'><iframe[^>]* src='([^']+)" % numero)
        if not url: continue

        servidor = servertools.get_server_from_url(url)
        if not servidor or servidor == 'directo': continue

        url = servertools.normalize_url(servidor, url)
        lang = scrapertools.find_single_match(enlace, "/img/flags/([^.']+)").lower()

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = IDIOMAS.get(lang, lang) ))

    matches = scrapertools.find_multiple_matches(bloque, "<li id='player-option-\d+'(.*?)</li>")
    for enlace in matches:
        # ~ logger.debug(enlace)
        dtype = scrapertools.find_single_match(enlace, "data-type='([^']+)")
        dpost = scrapertools.find_single_match(enlace, "data-post='([^']+)")
        dnume = scrapertools.find_single_match(enlace, "data-nume='([^']+)")
        if dnume == 'trailer': continue
        if not dtype or not dpost or not dnume: continue

        servidor = scrapertools.find_single_match(enlace, "<span class='server'>([^<.]+)")
        lang = scrapertools.find_single_match(enlace, "/img/flags/([^.']+)").lower()
        if not servidor or servidor == 'Desconocido' or not lang:
            # ~ <span class='title'>Subtitulado / STREAMTAPE</span>
            # ~ <span class='title'>SUB ESP ¦ DooD</span>
            aux = scrapertools.find_single_match(enlace, "<span class='title'>([^<]+)")
            sep = '/' if '/' in aux else '¦' if '¦' in aux else None
            if sep:
                if not lang: lang = aux.split(sep)[0].strip().lower()
                if not servidor or servidor == 'Desconocido': servidor = aux.split(sep)[1]

        servidor = corregir_servidor(servidor)

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', dtype = dtype, dpost = dpost, dnume = dnume,
                              referer = item.url, language = IDIOMAS.get(lang, lang) ))

    # Ver en línea
    bloque = scrapertools.find_single_match(data, "<div id='videos'(.*?)</table></div></div></div>")

    matches = scrapertools.find_multiple_matches(bloque, "<tr id='link-[^']+'>(.*?)</tr>")
    for enlace in matches:
        # ~ logger.debug(enlace)
        url = scrapertools.find_single_match(enlace, " href='([^']+)")
        servidor = corregir_servidor(scrapertools.find_single_match(enlace, "domain=([^'.]+)"))
        if not url or not servidor: continue

        uploader = scrapertools.find_single_match(enlace, "author/[^/]+/'>([^<]+)</a>")
        tds = scrapertools.find_multiple_matches(enlace, '<td>(.*?)</td>')
        quality = scrapertools.find_single_match(tds[1], "<strong class='quality'>([^<]+)")
        lang = tds[2].lower()

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url,
                              language = IDIOMAS.get(lang,lang), quality = quality, quality_num = puntuar_calidad(quality), other = uploader ))

    # Descarga ?
    # ~ bloque = scrapertools.find_single_match(data, "<div id='download'(.*?)</table></div></div></div>")

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if item.url and host in item.url:
        data = do_downloadpage(item.url)
        # ~ logger.debug(data)
        url = scrapertools.find_single_match(data, '<a id="link".*?href="([^"]+)')
        if url: 
            itemlist.append(item.clone( url=servertools.normalize_url(item.server, url) ))

    elif item.url and item.server:
        itemlist.append(item.clone())

    else:
        post = {'action': 'doo_player_ajax', 'post': item.dpost, 'nume': item.dnume, 'type': item.dtype}
        data = do_downloadpage(host + 'wp-admin/admin-ajax.php', post=post, headers={'Referer':item.referer})
        # ~ logger.debug(data)

        url = scrapertools.find_single_match(data, "src='([^']+)")
        if not url: url = scrapertools.find_single_match(data, 'src="([^"]+)')
        if not url: url = scrapertools.find_single_match(data, '"embed_url":"([^"]+)').replace('\\/', '/')
        if url: 
            if 'jwplayer' in url and 'source=' in url: 
                # Ej: https://www.dospelis.online/jwplayer-2/?source=12ZOwR37oT0mPRlEdceQ1f2t1jSac8H9U&id=127575&type=gdrive
                # Ej: https://www.dospelis.online/jwplayer-2/?source=https%3A%2F%2Fyoutu.be%2Fzcn89lxhEWk&id=71977&type=mp4
                if 'type=gdrive' in url: 
                    url = 'http://docs.google.com/get_video_info?docid=' + urllib.unquote(scrapertools.find_single_match(url, "source=([^&']+)"))
                else:
                    url = urllib.unquote(scrapertools.find_single_match(url, "source=([^&']+)"))

            elif 'streamcrypt.net/' in url: # Ej: https://streamcrypt.net/embed/streamz.cc/...
                url = scrapertools.decode_streamcrypt(url)
            # ~ logger.debug(url)

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

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)

    if item.search_type != 'all': # eliminar pelis/series según corresponda
        matches = list(filter(lambda x: ('class="movies"' in x and item.search_type == 'movie') or \
                                   ('class="tvshows"' in x and item.search_type == 'tvshow'), matches))

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
            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot} ))
        else:
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year, 'plot': plot} ))

        if len(itemlist) >= perpage: break


    tmdb.set_infoLabels(itemlist)

    # Subpaginación interna y/o paginación de la web
    buscar_next = True
    if num_matches > perpage: # subpaginación interna dentro de la página si hay demasiados items
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title='>> Página siguiente', page=item.page + 1, action='list_search', text_color='coral' ))
            buscar_next = False

    if buscar_next:
        next_page_link = scrapertools.find_single_match(data, '<a class=\'arrow_pag\' href="([^"]+)')
        if next_page_link:
            itemlist.append(item.clone( title='>> Página siguiente', url=next_page_link, page=0, action='list_search', text_color='coral' ))

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
