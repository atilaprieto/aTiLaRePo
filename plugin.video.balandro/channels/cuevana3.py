# -*- coding: utf-8 -*-

import re, urllib

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb

# ~ host = 'http://www.cuevana3.co/'
# ~ host = 'https://cuevana3.co/'
host = 'https://cuevana3.io/'

IDIOMAS = {'Latino':'Lat', 'Español':'Esp', 'Subtitulado':'VOSE'}


# ~ def item_configurar_proxies(item):
    # ~ plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    # ~ plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    # ~ return item.clone( title = 'Configurar proxies a usar ...', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )

# ~ def configurar_proxies(item):
    # ~ from core import proxytools
    # ~ return proxytools.configurar_proxies_canal(item.channel, host)

def do_downloadpage(url, post=None):
    url = url.replace('http://www.cuevana3.co/', 'https://cuevana3.co/') # por si viene de enlaces guardados
    url = url.replace('https://cuevana3.co/', 'https://cuevana3.io/') # por si viene de enlaces guardados
    data = httptools.downloadpage(url, post=post).data
    # ~ data = httptools.downloadpage_proxy('cuevana3', url, post=post).data
    return data


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
    
    itemlist.append(item.clone( title = 'Lista de películas', action = 'list_all', url = host + 'peliculas', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'estrenos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'peliculas-mas-valoradas', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'peliculas-mas-vistas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = host + 'peliculas-espanol', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = host + 'peliculas-latino', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'VOSE', action = 'list_all', url = host + 'peliculas-subtituladas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    # ~ itemlist.append(item_configurar_proxies(item))
    return itemlist

def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Últimas', action = 'list_all', url = host + 'serie', filtro = 'tabserie-1', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'serie', filtro = 'tabserie-2', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Ranking', action = 'list_all', url = host + 'serie', filtro = 'tabserie-3', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'serie', filtro = 'tabserie-4', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    # ~ itemlist.append(item_configurar_proxies(item))
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
        elif item.filtro == 'tabserie-3': post['action'] = 'cuevana_ajax_pagination_rating'
        elif item.filtro == 'tabserie-4': post['action'] = 'cuevana_ajax_pagination_view'
        data = do_downloadpage(host+'wp-admin/admin-ajax.php', post=urllib.urlencode(post))

    else:
        data = do_downloadpage(item.url)
        if item.filtro: # Para series limitar según últimas, estrenos, ranking, mas vistas
            data = scrapertools.find_single_match(data, '<div\s*id=%s(.*?)</nav>\s*</div>' % item.filtro)
    # ~ logger.debug(data)

    matches = re.compile('<li\s*class="[^"]*TPostMv">(.*?)</li>', re.DOTALL).findall(data)
    for article in matches:
        tipo = 'tvshow' if 'class=Qlty>SERIE' in article else 'movie'
        if item.search_type not in ['all', tipo]: continue
        sufijo = '' if item.search_type != 'all' else tipo
        
        url = scrapertools.find_single_match(article, '\s*href=([^ >]+)')
        if '/pagina-ejemplo' in url: continue
        thumb = scrapertools.find_single_match(article, 'data-src=([^ >]+)')
        title = scrapertools.find_single_match(article, '<h2 class="Title">([^<]+)</h2>')
        year = scrapertools.find_single_match(article, '<span\s*class=Year>(\d+)</span>')
        qlty = scrapertools.find_single_match(article, '<span\s*class=Qlty>([^<]+)</span>')
        
        if tipo == 'movie':
            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, fmt_sufijo=sufijo, 
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))
        else:
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, 
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    next_page_link = scrapertools.find_single_match(data, ' rel="next" href="([^"]+)"')
    if next_page_link == '':
        next_page_link = scrapertools.find_single_match(data, '\s*href=([^ >]+) class="next')
    if next_page_link:
        if not item.filtro:
            itemlist.append(item.clone( title='>> Página siguiente', url=next_page_link, action='list_all' ))
        else:
            pagina = 2 if not item.page else item.page + 1
            itemlist.append(item.clone( title='>> Página siguiente', url=next_page_link, action='list_all', page=pagina ))
    
    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    
    patron = '<option\s*value=(\d+)>Temporada \d+</option>'
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

    if item.contentSeason: # reducir datos a la temporada pedida
        data = scrapertools.find_single_match(data, '<ul\s*id=season-%d(.*?)</ul>' % item.contentSeason)

    patron = '<li.*?<a\s*href=([^ >]+)>(.*?)</li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, datos in matches:
        try:
            season, episode = scrapertools.find_single_match(url, '-(\d+)x(\d+)$')
        except:
            continue

        title = scrapertools.find_single_match(datos, '<h2[^>]*>(.*?)</h2>')
        thumb = scrapertools.find_single_match(datos, 'data-src=([^ >]+)"')

        itemlist.append(item.clone( action='findvideos', title = title, thumbnail=thumb, url = url,
                                    contentType = 'episode', contentSeason = season, contentEpisodeNumber = episode ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


# Asignar un numérico según las calidades del canal, para poder ordenar por este valor
def puntuar_calidad(txt):
    orden = ['Cam', 'WEB-S', 'DVD-S', 'TS-HQ', 'DVD', 'DvdRip', 'HD']
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
            # ~ logger.info(url)
            url = url.replace('#Synchronization+Service', '')
            itemlist.append(Item( channel = item.channel, action = 'play', other = option,
                                  title = '', url = url, referer = item.url,
                                  language = IDIOMAS.get(language, language), quality = quality, quality_num = puntuar_calidad(quality)
                           ))

    # Enlaces de descarga (sólo uptobox)
    patron = 'Uptobox</td><td>([^<]*)</td><td><span>([^<]*)</span></td><td><a\s*rel=nofollow target=_blank href="([^"]+)" class="Button STPb">Descargar</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for language, quality, url in matches:
        # ~ logger.debug('%s %s %s' % (language, quality, url))
        if url.startswith('/'): url = 'https:' + url
        itemlist.append(Item( channel = item.channel, action = 'play', other = 'D', server = 'uptobox',
                              title = '', url = url, referer = item.url,
                              language = IDIOMAS.get(language, language), quality = quality, quality_num = puntuar_calidad(quality)
                       ))


    itemlist = servertools.get_servers_itemlist(itemlist)

    # Dejar desconocidos como directos para resolverse en el play
    for it in itemlist:
        if it.server == 'desconocido' and '//api.cuevana3' in it.url:
            it.server = 'fembed' if '/fembed/?' in it.url else ''
        elif it.server == 'desconocido' and 'openloadpremium.com/' in it.url:
            it.server = 'm3u8hls'

    return itemlist

def play(item):
    logger.info()
    itemlist = []

    if '//api.cuevana3' in item.url:

        if 'file=' in item.url:
            fid = scrapertools.find_single_match(item.url, "file=([^&]+)")
            url = 'https://api.cuevana3.io/stream/plugins/gkpluginsphp.php'
            data = httptools.downloadpage(url, post=urllib.urlencode({'link': fid})).data.replace('\\/', '/')
            # ~ logger.debug(data)

            enlaces = scrapertools.find_multiple_matches(data, '"link":"([^"]+)"([^}]*)')
            for url, resto in enlaces:
                # ~ if 'player.php?id=' in url: continue # acaba en un m3u8 no reproducible por kodi
                if 'player.php?id=' in url:
                    url = url.replace('player.php?id=', 'index/').replace('&hlsfe=yes', '.m3u8')
                    data = httptools.downloadpage(url).data
                    matches = scrapertools.find_multiple_matches(data, 'RESOLUTION=\d+x(\d+)\s*(.*?\.m3u8)')
                    if matches:
                        # ~ for res, url in matches:
                            # ~ itemlist.append([res, url])
                        for res, url in sorted(matches, key=lambda x: int(x[0]), reverse=True):
                            itemlist.append(item.clone(url = url, server = 'm3u8hls'))
                            break
                        return itemlist

                elif 'openloadpremium.com/embed/' in url:
                    # ~ data = httptools.downloadpage(url).data
                    # ~ logger.debug(data)
                    continue # no encontrado ningún ejemplo válido, TODO...

                else:
                    lbl = scrapertools.find_single_match(resto, '"label":"([^"]+)')
                    if not lbl: lbl = scrapertools.find_single_match(resto, '"type":"([^"]+)')
                    if not lbl: lbl = 'mp4'
                    itemlist.append([lbl, url])
                
            itemlist.sort(key=lambda it: int(it[0].replace('p','')) if it[0].endswith('p') else it[0])

        elif 'fembed/?h=' in item.url or 'uptobox/goto.php?h=' in item.url:
            fid = scrapertools.find_single_match(item.url, "h=([^&]+)")
            serv = 'fembed' if 'fembed/?h=' in item.url else 'uptobox'
            data = httptools.downloadpage('https://api.cuevana3.io/'+serv+'/api.php', post=urllib.urlencode({'h': fid})).data.replace('\\/', '/')
            # ~ logger.debug(data)
            url = scrapertools.find_single_match(data, '"url":"([^"]+)')
            if url:
                itemlist.append(item.clone(url=url))
            
        elif 'h=' in item.url:
            fid = scrapertools.find_single_match(item.url, "h=([^&]+)")
            resp = httptools.downloadpage('https://api.cuevana3.io/rr/gotogd.php?h=%s' % fid, follow_redirects=False)
            if 'location' in resp.headers:
                fid = scrapertools.find_single_match(resp.headers['location'], "id=([^&]+)")
                if fid:
                    url = resp.headers['location'].replace('public/dist/index.html?id=', 'hls/') + '/' + fid + '.playlist.m3u8'
                    itemlist.append(['m3u8', url])

    elif 'openloadpremium.com/' in item.url and '/player.php?' in item.url:
        data = httptools.downloadpage(item.url, headers={'Referer': item.referer}).data
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
