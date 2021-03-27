# -*- coding: utf-8 -*-

import re, base64

from platformcode import logger
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://allpeliculas.nu/'

perpage = 18


# ~ def item_configurar_proxies(item):
    # ~ plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    # ~ plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    # ~ return item.clone( title = 'Configurar proxies a usar ...', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )

# ~ def configurar_proxies(item):
    # ~ from core import proxytools
    # ~ return proxytools.configurar_proxies_canal(item.channel, host)


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    url = url.replace('allpeliculas.tv', 'allpeliculas.nu')

    data = httptools.downloadpage(url, post=post, headers=headers).data
    # ~ data = httptools.downloadpage_proxy('allpeliculas', url, post=post, headers=headers).data
    return data


def mainlist(item):
    return mainlist_pelis(item)

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host ))
    # ~ itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'genero/estrenos/' ))
    # ~ itemlist.append(item.clone( title = 'Netflix', action = 'list_all', url = host + 'genero/netflix/' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))
    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone ( title = 'Por año', action = 'anios', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    # ~ itemlist.append(item_configurar_proxies(item))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, 'Géneros</a>\s*<ul(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)"[^>]*>([^<]+)')

    for url, title in matches:
        if 'genero/estrenos/' in url or 'genero/netflix/' in url: continue
        if url.startswith('/'): url = host + url[1:]
        if '/genero/' not in url: url = url.replace(host, host + 'genero/')

        itemlist.append(item.clone( action='list_all', title=title, url=url ))

    itemlist.append(item.clone( action = 'list_all', title = 'Bélica', url = host + 'genero/belica/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Biografía', url = host + 'genero/biografia/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Historia', url = host + 'genero/historia/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Western', url = host + 'genero/western/' ))

    return sorted(itemlist, key=lambda it: it.title)


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = host + 'pelicula/tag/espanol/' ))
    itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = host + 'pelicula/tag/latino/' ))
    itemlist.append(item.clone( title = 'Subtitulado', action = 'list_all', url = host + 'pelicula/tag/subtitulado/' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1953, -1):
        itemlist.append(item.clone( title=str(x), url= host + 'pelicula/year_relase/' + str(x) + '/', action='list_all' ))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    post_q = '{"posts_per_page":%s, "comments_per_page":0}' % perpage
    if '/genero/' in item.url:
        aux = scrapertools.find_single_match(item.url, '/genero/([^/]+)')
        post_q = post_q.replace('}', ',"category_name":"%s"}' % aux)
    elif '/year_relase/' in item.url:
        aux = scrapertools.find_single_match(item.url, '/year_relase/([^/]+)')
        post_q = post_q.replace('}', ',"year_relase":"%s"}' % aux)
    elif '/tag/' in item.url:
        aux = scrapertools.find_single_match(item.url, '/tag/([^/]+)')
        post_q = post_q.replace('}', ',"tag":"%s"}' % aux)
    elif '/search/' in item.url:
        aux = scrapertools.find_single_match(item.url, '/search/([^/]+)')
        post_q = post_q.replace('}', ',"s":"%s"}' % aux)

    post = {'action':'loadmore', 'page':item.page, 'query':post_q}
    data = do_downloadpage(host + 'wp-admin/admin-ajax.php', post=post)
    # ~ data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    matches = re.compile('<div class="col-mt-5 postsh">\s*<div class="poster-media-card">\s*<a(.*?)</a>', re.DOTALL).findall(data)
    num_matches = len(matches)

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)')
        title = scrapertools.find_single_match(article, ' title="([^"]+)')
        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, ' loading="lazy".*? src="([^"]+)"')

        year = scrapertools.find_single_match(article, 'data-year="(\d{4})')
        if not year: year = scrapertools.find_single_match(title, '\((\d{4})\)')
        if year:
            title = title.replace('(%s)' % year, '').strip()
        else:
            year = '-'

        langs = []
        if ' alt="Castellano"' in article: langs.append('Esp')
        if ' alt="Latino"' in article: langs.append('Lat')
        if ' alt="Subtitulado"' in article: langs.append('Vose')

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages=','.join(langs),
                                    contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if num_matches >= perpage:
        itemlist.append(item.clone( title='>> Página siguiente', page=item.page + 1, action='list_all', text_color='coral' ))

    return itemlist


def puntuar_calidad(txt):
    txt = txt.replace(' ', '').replace('-', '').lower()
    orden = ['cam', 'ts', 'dvd', 'dvd+', 'hd', 'hd+', 'hd1080p']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'Español': 'Esp', 'Latino': 'Lat', 'Subtitulado': 'Vose'}

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    # Enlaces en embeds
    patron = '<a href="#embed\d+" data-src="([^"]+)" class="([^"]+)"(.*?)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for urlcod, lang, resto in matches:
        if urlcod.startswith('//'): urlcod = 'https:' + urlcod
        elif urlcod.startswith('/'): urlcod = host + urlcod[1:]
        cod = urlcod.replace(host + 'replayer/', '').split('RRRRR')[0]
        # ~ logger.info('%s %s' % (cod, urlcod))
        numpad = len(cod) % 4
        if numpad > 0: cod += 'R' * (4 - numpad)

        try:
            url = base64.b64decode(cod)
            if numpad > 0: url = url[:-(4 - numpad)]
        except:
            url = None
        
        if not url: 
            logger.info('No detectada url. %s %s' % (cod, urlcod))
            continue
        if not isinstance(url, str):
            url = url.decode("utf-8", "strict")
        if "streamcrypt.net/embed/streamz" in url:
            url = httptools.downloadpage(url).url
        logger.error(url)
        servidor = servertools.get_server_from_url(url)
        if not servidor or (servidor == 'directo' and 'storage.googleapis.com/' not in url): 
            logger.info('No detectado servidor, url: %s' % url)
            continue
        url = servertools.normalize_url(servidor, url)

        qlty = scrapertools.find_single_match(resto, '([^>]+)</div>$')

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, 
                              language = IDIOMAS.get(lang, lang), quality = qlty, quality_num = puntuar_calidad(qlty), other='e' ))

    # Enlaces en descargas
    bloque = scrapertools.find_single_match(data, 'id="dlnmt"(.*?)</table>')
    matches = re.compile('<tr>(.*?)</tr>', re.DOTALL).findall(bloque)
    for lin in matches:
        if '<th' in lin: continue

        tds = scrapertools.find_multiple_matches(lin, '<td[^>]*>(.*?)</td>')
        url = scrapertools.find_single_match(tds[0], ' href="([^"]+)')
        servidor = scrapertools.find_single_match(tds[1], '<span>(.*?)</span>')
        lang = tds[2]
        qlty = tds[3]
        if '/link/?go=' in url: url = url.split('/link/?go=')[1]
        if not url or not servidor: continue

        itemlist.append(Item( channel = item.channel, action = 'play', server = servertools.corregir_servidor(servidor), title = '', url = url, 
                              language = IDIOMAS.get(lang, lang), quality = qlty, quality_num = puntuar_calidad(qlty), other='d' ))

    return itemlist


def search(item, texto):
    logger.info("texto: %s" % texto)
    try:
        item.url = host + 'search/' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
