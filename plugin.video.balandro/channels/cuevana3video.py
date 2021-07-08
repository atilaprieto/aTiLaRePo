# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www1.cuevana3.video'

perpage = 22


# ~ def item_configurar_proxies(item):
    # ~ plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    # ~ plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    # ~ return item.clone( title = 'Configurar proxies a usar ...', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )

# ~ def configurar_proxies(item):
    # ~ from core import proxytools
    # ~ return proxytools.configurar_proxies_canal(item.channel, host)

def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    resp = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror)
    # ~ resp = httptools.downloadpage_proxy('cuevana3video', url, post=post, headers=headers, raise_weberror=raise_weberror)

    return resp.data


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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/peliculas', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + '/estrenos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + '/peliculas-mas-vistas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    # ~ itemlist.append(item_configurar_proxies(item))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catalogo', action = 'list_all', url = host + '/serie', filtro = 'tabserie-1', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + '/serie', filtro = 'tabserie-4', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    # ~ itemlist.append(item_configurar_proxies(item))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data,'href="#">Géneros</a>(.*?)<li id="menu-item-1954"')
    matches = scrapertools.find_multiple_matches(bloque,'<a href=".*?">.*?</a>')

    for match in matches:
        url = scrapertools.find_single_match(match,'<a href="(.*?)">')
        title = scrapertools.find_single_match(match,'>(.*?)</a>')

        itemlist.append(item.clone( title = title, url = host + url , action = 'list_all', search_type = item.search_type ))

    return sorted(itemlist, key=lambda it: it.title)


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    if item.filtro: # series limitar
        if item.pageser: # paginaciones series
            url = host + '/serie?action=cuevana_ajax_pagination&page=' + str(item.pageser)
            data = do_downloadpage(url, headers={'Referer': url})
        else:
            data = do_downloadpage(item.url)

        data = scrapertools.find_single_match(data, '<div\s*id="%s"(.*?)</nav>\s*</div>' % item.filtro)
    else:
        data = do_downloadpage(item.url)

    # ~ logger.debug(data)

    matches = re.compile('<li\s*class="[^"]*TPostMv">(.*?)</li>', re.DOTALL).findall(data)
    num_matches = len(matches)

    for article in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(article, '\s*href=(?:"|)([^ >"]+)')
        if '/pagina-ejemplo' in url: continue

        tipo = 'tvshow' if '/serie/' in url else 'movie'
        if item.search_type not in ['all', tipo]: continue

        sufijo = '' if item.search_type != 'all' else tipo

        thumb = scrapertools.find_single_match(article, 'data-src="([^ >]+)"')
        if not thumb: thumb = scrapertools.find_single_match(article, ' src=(?:"|)([^ >"]+)')

        title = scrapertools.find_single_match(article, '<h2 class="Title">([^<]+)</h2>').strip()
        qlty = scrapertools.find_single_match(article, '<span\s*class=(?:"|)Qlty(?:"|)>([^<]+)</span>')
        plot = scrapertools.find_single_match(article, '<p>(.*?)</p>')

        url = host + url

        if tipo == 'movie':
            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail='https:'+ thumb, qualities=qlty, fmt_sufijo=sufijo, 
                                        contentType='movie', contentTitle=title, infoLabels={'year': '-', 'plot': plot} ))
        else:
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, 
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': '-', 'plot': plot} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    buscar_next = True
    if num_matches > perpage:
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title = '>> Página siguiente', page = item.page + 1, action = 'list_all', text_color='coral' ))
            buscar_next = False

    if buscar_next:
        if item.filtro:
           if itemlist:
                pagina = 2 if not item.pageser else item.pageser + 1
                itemlist.append(item.clone( title = '>> Página siguiente', action = 'list_all', pageser = pagina, text_color='coral' ))
        else:
           if '<nav class="navigation pagination">' in data:
               bloque_next = scrapertools.find_single_match(data, '<nav class="navigation pagination">(.*?)</nav>')
               next_page_link = scrapertools.find_single_match(bloque_next, "class='page-link current'>.*?</a><a href='(.*?)'")

               if next_page_link:
                   if not '?page=' in item.url:
                       next_page_link = item.url + next_page_link
                   else:
                       ant_url = scrapertools.find_single_match(item.url, "(.*?)page=")
                       ant_url = ant_url.replace('?', '')
                       next_page_link = ant_url + next_page_link

                   itemlist.append(item.clone( title = '>> Página siguiente', url = next_page_link, page = 0, action = 'list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    patron = '<option\s*value="(\d+)".*?Temporada'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for numtempo in matches:
        title = 'Temporada ' + numtempo

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&'), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action='episodios', title=title, contentType='season', contentSeason=numtempo, page=0 ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


# Si una misma url devuelve los episodios de todas las temporadas, definir rutina tracking_all_episodes para acelerar el scrap en trackingtools.
def tracking_all_episodes(item):
    return episodios(item)

def episodios(item):
    logger.info()
    itemlist=[]

    if not item.page: item.page = 0
    perpage = 50

    data = do_downloadpage(item.url)

    if item.contentSeason: # reducir datos a la temporada pedida
        data = scrapertools.find_single_match(data, '<ul\s*id="season-' + str(item.contentSeason) + '(.*?)</ul>')

    patron = '<li class="xxx TPostMv">.*?<a href="(.*?)">(.*?)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, datos in matches[item.page * perpage:]:
        try:
            season, episode = scrapertools.find_single_match(datos, '<span class="Year">(.*?)x(.*?)</span>')
        except:
            continue

        if item.contentSeason:
           if not str(item.contentSeason) == str(season): continue

        title = scrapertools.find_single_match(datos, '<h2[^>]*>(.*?)</h2>')

        thumb = scrapertools.find_single_match(datos, 'data-src=([^ >]+)"')
        if  thumb.startswith('//'): thumb = 'https:' + thumb

        url = host + url

        itemlist.append(item.clone( action='findvideos', title = title, thumbnail=thumb, url = url,
                                    contentType = 'episode', contentSeason = season, contentEpisodeNumber = episode ))

        if len(itemlist) >= perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if len(matches) > (item.page + 1) * perpage:
        itemlist.append(item.clone( title=">> Página siguiente", action="episodios", page=item.page + 1, text_color='coral' ))

    return itemlist


# Asignar un numérico según las calidades del canal, para poder ordenar por este valor
def puntuar_calidad(txt):
    orden = ['Cam', 'WEB-S', 'DVD-S', 'TS-HQ', 'DVD', 'DvdRip', 'HD', 'FullHD1080p']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1

def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'Latino': 'Lat', 'Castellano': 'Esp', 'Subtitulado': 'Vose'}

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    patron = '<ul class="anime_muti_link server-item-(.*?)</ul>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for option in matches:
        links = scrapertools.find_multiple_matches(option, '<li data-(.*?)</li>')

        for link in links:
            url = scrapertools.find_single_match(link, 'video="(.*?)"')
            lang = scrapertools.find_single_match(link,'<span class="cdtr">.*?<span>.*?-(.*?)-.*?</span>').strip()

            qlty = scrapertools.find_single_match(link,'<span class="cdtr">.*?<span>.*?-.*?-(.*?)</span>').strip()
            quality_num = puntuar_calidad(qlty)
            if quality_num == 0: qlty = ''

            if url.startswith('//'): url = 'https:' + url

            if url:
                servidor = servertools.get_server_from_url(url)
                url = servertools.normalize_url(servidor, url)

                if servidor == 'directo':
                    link_other = normalize_other(url)
                    if link_other == '': continue
                else:
                    link_other = ''

                if not config.get_setting('developer_mode', default=False):
                   if link_other == 'Plus': continue
                   elif link_other == 'hydrax': continue

                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, other = link_other, title = '', url = url, referer = item.url,
                                      language = IDIOMAS.get(lang, lang), quality = qlty, quality_num = quality_num ))

    if '<li class="downloadopt">' in data:
        url = scrapertools.find_single_match(data, '<li class="downloadopt">.*?<a href="(.*?)"')
        if url:
            if url.startswith('//'): url = 'https:' + url

            servidor = servertools.get_server_from_url(url)
            url = servertools.normalize_url(servidor, url)

            if servidor == 'directo':
                link_other = normalize_other(url)
            else:
                link_other = ''

            if not link_other == '':
                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, other = link_other, title = '', url = url, referer = item.url,
                                      quality = 'HD' ))

    return itemlist


def normalize_other(url):
    link_other = ''
    url = url.lower()

    if 'pelisplus' in url: link_other = 'Plus'
    elif 'peliscloud' in url: link_other = 'Cloud'
    elif 'damedame' in url: link_other = 'Dame'
    elif 'hydrax' in url: link_other = 'Hydrax'
    else:
       if config.get_setting('developer_mode', default=False):
           try:
              link_other = url.split('//')[1]
              link_other = link_other.split('/')[0]
           except:
              link_other = url

    return link_other


def play(item):
    logger.info()
    itemlist = []
    # ~ logger.debug(item.url)

    servidor = item.server
    url = item.url

    if servidor and servidor != 'directo':
        itemlist.append(item.clone(server = servidor, url = url))

    if item.other == 'Plus':
        data = do_downloadpage(item.url)

        if item.url.startswith('https://pelisplus.icu/download'):
            matches = scrapertools.find_multiple_matches(data, '<div class="dowload".*?href="(.*?)"')

            for url in matches:
                if not 'https://xstreamcdn.com/f/' in url: continue

                url = url.replace('https://xstreamcdn.com/f/', '')

                servidor = servertools.get_server_from_url(url)
                url = servertools.normalize_url(servidor, url)

                if servidor and servidor != 'directo':
                    itemlist.append(item.clone(url=url , server=servidor))
                    return itemlist

        matches = scrapertools.find_multiple_matches(data, 'data-video="(.*?)"')

        for url in matches:
            if 'https://damedamehoy.xyz/embed.html#' in url:
                url = url.replace('https://damedamehoy.xyz/embed.html#', 'https://damedamehoy.xyz/details.php?v=')
                data = do_downloadpage(url, raise_weberror=False )

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

    elif item.other == 'Cloud':
        data = do_downloadpage(url)
        matches = scrapertools.find_multiple_matches(data, "var urlVideo = '(.*?)'")

        for url in matches:
            if url == '//': continue

            servidor = 'directo'
            if '/hls/' in url: servidor = 'm3u8hls'

            itemlist.append(item.clone(url=url , server=servidor))
            return itemlist

    elif item.other == 'Dame':
        url = item.url.replace('https://damedamehoy.xyz/embed.html#', 'https://damedamehoy.xyz/details.php?v=')
        data = do_downloadpage(url, raise_weberror=False)
        url = scrapertools.find_single_match(data, '"file":"(.*?)"')
        url = url.replace('\\/', '/')

        itemlist.append(item.clone(url=url , server='directo'))
        return itemlist

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '/search.html?keyword=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
