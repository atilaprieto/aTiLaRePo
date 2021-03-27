# -*- coding: utf-8 -*-

import re

from platformcode import logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://cuevana3.io/'

IDIOMAS = {'Latino': 'Lat', 'Español': 'Esp', 'Subtitulado': 'Vose'}


def item_configurar_proxies(item):
    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = 'Configurar proxies a usar ...', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)

def do_downloadpage(url, post=None, headers=None, follow_redirects=True, only_headers=False):
    # ~ por si viene de enlaces guardados
    url = url.replace('http://www.cuevana3.co/', 'https://cuevana3.io/')
    url = url.replace('https://cuevana3.co/', 'https://cuevana3.io/')

    # ~ resp = httptools.downloadpage(url, post=post, headers=headers, follow_redirects=follow_redirects, only_headers=only_headers)
    resp = httptools.downloadpage_proxy('cuevana3', url, post=post, headers=headers, follow_redirects=follow_redirects, only_headers=only_headers)

    if only_headers: return resp.headers
    return resp.data


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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'estrenos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'peliculas-mas-valoradas', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'peliculas-mas-vistas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    itemlist.append(item_configurar_proxies(item))
    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catalogo', action = 'list_all', url = host + 'serie', filtro = 'tabserie-1', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'serie', filtro = 'tabserie-2', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'serie', filtro = 'tabserie-3', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'serie', filtro = 'tabserie-4', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    itemlist.append(item_configurar_proxies(item))
    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = host + 'peliculas-espanol', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = host + 'peliculas-latino', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Subtitulado', action = 'list_all', url = host + 'peliculas-subtituladas', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    matches = re.compile('/(category/[^ >]+)>([^<]+)</a></li>', re.DOTALL).findall(data)
    for url, title in matches:
        itemlist.append(item.clone( title=title, url=host + url, action='list_all', search_type = item.search_type ))

    itemlist.append(item.clone( title='Suspense', url=host + 'category/suspense', action='list_all', search_type = item.search_type ))
    itemlist.append(item.clone( title='Western', url=host + 'category/western', action='list_all', search_type = item.search_type ))

    return sorted(itemlist, key=lambda it: it.title)


def list_all(item):
    logger.info()
    itemlist = []

    if item.page: # paginaciones ajax para series
        post = {'page': item.page}
        if item.filtro == 'tabserie-1': post['action'] = 'cuevana_ajax_pagination'
        elif item.filtro == 'tabserie-2': post['action'] = 'cuevana_ajax_pagination_estreno'
        elif item.filtro == 'tabserie-3': post['action'] = 'cuevana_ajax_pagination_rating'
        elif item.filtro == 'tabserie-4': post['action'] = 'cuevana_ajax_pagination_view'
        data = do_downloadpage(host+'wp-admin/admin-ajax.php', post=post)

    else:
        data = do_downloadpage(item.url)
        if item.filtro: # Para series limitar según últimas, estrenos, ranking, mas vistas
            data = scrapertools.find_single_match(data, '<div\s*id=%s(.*?)</nav>\s*</div>' % item.filtro)
    # ~ logger.debug(data)

    matches = re.compile('<li\s*class="[^"]*TPostMv">(.*?)</li>', re.DOTALL).findall(data)
    for article in matches:
        tipo = 'tvshow' if 'class=Qlty>SERIE' in article or 'class="Qlty">SERIE' in article else 'movie'
        if item.search_type not in ['all', tipo]: continue
        sufijo = '' if item.search_type != 'all' else tipo

        url = scrapertools.find_single_match(article, '\s*href=(?:"|)([^ >"]+)')
        if '/pagina-ejemplo' in url: continue
        thumb = scrapertools.find_single_match(article, 'data-src=([^ >]+)')
        if not thumb: thumb = scrapertools.find_single_match(article, ' src=(?:"|)([^ >"]+)')
        title = scrapertools.find_single_match(article, '<h2 class="Title">([^<]+)</h2>')
        year = scrapertools.find_single_match(article, '<span\s*class=(?:"|)Year(?:"|)>(\d+)</span>')
        qlty = scrapertools.find_single_match(article, '<span\s*class=(?:"|)Qlty(?:"|)>([^<]+)</span>')

        if tipo == 'movie':
            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, fmt_sufijo=sufijo, 
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))
        else:
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, 
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if item.filtro:
       if itemlist:
            pagina = 2 if not item.page else item.page + 1
            itemlist.append(item.clone( title='>> Página siguiente', action='list_all', page=pagina, text_color='coral' ))
    else:
       next_page_link = scrapertools.find_single_match(data, ' rel="next" href="([^"]+)"')
       if next_page_link == '':
           next_page_link = scrapertools.find_single_match(data, '\s*href=(?:"|)([^ >"]+) class="next')

       if next_page_link:
           itemlist.append(item.clone( title='>> Página siguiente', url=next_page_link, action='list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('<option\s*value=(\d+)>Temporada \d+</option>', re.DOTALL).findall(data)

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
        data = scrapertools.find_single_match(data, '<ul\s*id=season-' + str(item.contentSeason) + '(.*?)</ul>')

    patron = '<li.*?<a\s*href=([^ >]+)>(.*?)</li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, datos in matches[item.page * perpage:]:
        try:
            season, episode = scrapertools.find_single_match(url, '-(\d+)x(\d+)$')
        except:
            continue

        title = scrapertools.find_single_match(datos, '<h2[^>]*>(.*?)</h2>')
        thumb = scrapertools.find_single_match(datos, 'data-src=([^ >]+)"')

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

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    patron = 'TPlayerNv=Opt(\w\d+).*?img\s*src=(.*?)<span>\d+ - (.*?) - ([^<]+)<'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for option, url_data, language, quality in matches:
        # ~ logger.debug('%s %s %s %s' % (option, url_data, language, quality))

        url = scrapertools.find_single_match(data, 'id=Opt%s><iframe.*? data-src=(?:"|)([^ >"]+)' % option)
        if url.startswith('/'): url = 'https:' + url
        # ~ if '/fembed/?' in url:
            # ~ url = scrapertools.find_single_match(url_data, 'domain=([^"]+)"')

        if url and 'youtube' not in url:
            # ~ logger.info('%s %s' % (option, url))
            url = url.replace('#Synchronization+Service', '')
            itemlist.append(Item( channel = item.channel, action = 'play', other = option, title = '', url = url, referer = item.url,
                                  language = IDIOMAS.get(language, language), quality = quality, quality_num = puntuar_calidad(quality) ))

    # Enlaces de descarga (sólo uptobox)
    patron = 'Uptobox</td><td>([^<]*)</td><td><span>([^<]*)</span></td><td><a\s*rel=nofollow target=_blank href="([^"]+)" class="Button STPb">Descargar</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for language, quality, url in matches:
        # ~ logger.info('%s %s %s' % (language, quality, url))
        if url.startswith('/'): url = 'https:' + url
        itemlist.append(Item( channel = item.channel, action = 'play', other = 'D', server = 'uptobox', title = '', url = url, referer = item.url,
                              language = IDIOMAS.get(language, language), quality = quality, quality_num = puntuar_calidad(quality) ))

    itemlist = servertools.get_servers_itemlist(itemlist)
    # Dejar desconocidos como directos para resolverse en el play
    for it in itemlist:
        if it.server == 'desconocido' and ('//api.cuevana3' in it.url or '//damedamehoy.' in it.url):
            it.server = 'fembed' if '/fembed/?' in it.url else 'directo' if '//damedamehoy.' in it.url else ''
        elif it.server == 'desconocido' and 'openloadpremium.com/' in it.url:
            it.server = 'm3u8hls'

    return itemlist

def resuelve_damedamehoy(dame_url):
    dame_url = dame_url
    data = do_downloadpage(dame_url)

    # ~ logger.debug(data)
    url = scrapertools.find_single_match(data, 'file:\s*"([^"]+)')
    if not url:
        checkUrl = dame_url.replace('embed.html#', 'details.php?v=')
        data = do_downloadpage(checkUrl, headers={'Referer': dame_url})
        # ~ logger.debug(data)
        url = scrapertools.find_single_match(data, '"file":\s*"([^"]+)').replace('\\/', '/')
    return url

def play(item):
    logger.info()
    itemlist = []
    # ~ logger.debug(item.url)

    if '//damedamehoy.' in item.url:
        url = resuelve_damedamehoy(item.url)
        if url: itemlist.append(['mp4', url])
        return itemlist

    if '//api.cuevana3' in item.url:

        if 'file=' in item.url:
            fid = scrapertools.find_single_match(item.url, "file=([^&]+)").replace('\\/', '/')
            url = 'https://api.cuevana3.io/stream/plugins/gkpluginsphp.php'
            data = do_downloadpage(url, post={'link': fid})
            # ~ logger.debug(data)

            enlaces = scrapertools.find_multiple_matches(data, '"link":"([^"]+)"([^}]*)')
            for url, resto in enlaces:
                if 'player.php?id=' in url:
                    url = url.replace('player.php?id=', 'index/').replace('&hlsfe=yes', '.m3u8')
                    data = do_downloadpage(url)
                    matches = scrapertools.find_multiple_matches(data, 'RESOLUTION=\d+x(\d+)\s*(.*?\.m3u8)')
                    if matches:
                        # ~ for res, url in matches:
                            # ~ itemlist.append([res, url])
                        for res, url in sorted(matches, key=lambda x: int(x[0]), reverse=True):
                            itemlist.append(item.clone(url = url, server = 'm3u8hls'))
                            break
                        return itemlist

                elif 'openloadpremium.com/embed/' in url:
                    # ~ data = do.downloadpage(url)
                    # ~ logger.debug(data)
                    continue # no encontrado ningún ejemplo válido, TODO...

                else:
                    lbl = scrapertools.find_single_match(resto, '"label":"([^"]+)')
                    if not lbl: lbl = scrapertools.find_single_match(resto, '"type":"([^"]+)')
                    if not lbl: lbl = 'mp4'
                    itemlist.append([lbl, url])

            itemlist.sort(key=lambda it: int(it[0].replace('p','')) if it[0].endswith('p') else it[0])

        elif 'h=' in item.url:
            fid = scrapertools.find_single_match(item.url, "h=([^&]+)")
            if 'https://api.cuevana3.io/sc/index.php?h=' in item.url:
                api_url = 'https://api.cuevana3.io/sc/r.php'
                api_post = 'h='+fid
            elif 'https://api.cuevana3.io/ir/goto_ddh.php' in item.url:
                api_url = 'https://api.cuevana3.io/ir/redirect_ddh.php'
                api_post = 'url='+fid
            else:
                api_url = 'https://api.cuevana3.io/ir/rd.php'
                api_post = 'url='+fid

            url = do_downloadpage(api_url, post=api_post, headers={'Referer': item.url}, follow_redirects=False, only_headers=True).get('location', '')

            # ~ logger.debug(resp.data)
            if '//damedamehoy.' in url:
                url = resuelve_damedamehoy(url)
                if url: itemlist.append(['mp4', url])
            else:
                servidor = servertools.get_server_from_url(url)
                if servidor != 'directo':
                    url = servertools.normalize_url(servidor, url)
                    itemlist.append(item.clone( url = url, server = servidor ))
                else:
                    fid = scrapertools.find_single_match(url, "id=([^&]+)")
                    if fid:
                        url = url.replace('public/dist/index.html?id=', 'hls/') + '/' + fid + '.playlist.m3u8'
                        itemlist.append(['m3u8', url])

    elif 'openloadpremium.com/' in item.url and '/player.php?' in item.url:
        data = do_downloadpage(item.url, headers={'Referer': item.referer})
        # ~ logger.debug(data)
        url = scrapertools.find_single_match(data, '"file": "([^"]+)')
        if url:
            # ~ itemlist.append(item.clone(url = url))
            if 'openloadpremium.com/mp4/' in url and 'hash=' in url: 
                itemlist.append(item.clone(url = url+'|Referer='+item.url, server='directo'))
            else:
                itemlist.append(item.clone(url = url))

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

