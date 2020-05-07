# -*- coding: utf-8 -*-

import re

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools

host = 'https://zoowoman.website/wp/'

IDIOMAS = {'es':'Esp', 'ar':'Lat', 'pe':'Lat', 'mx':'Lat', '?':'?',
           'iberian spanish':'Esp', 'español latino':'Lat', 'vose':'VOSE'}


def mainlist(item):
    return mainlist_pelis(item)

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Últimas películas', action = 'list_all', url = host + 'movies/' ))
    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'tendencias/' ))
    itemlist.append(item.clone( title = 'Mejor valoradas', action = 'list_all', url = host + 'calificaciones/' ))
    itemlist.append(item.clone( title = 'Las 1001 que hay que ver', action='list_all', url = host + 'genre/1001-peliculas-que-ver/' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por subgénero', action = 'subgeneros', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por época', action = 'epocas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por directores/directoras', action = 'directores' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)
    
    data = httptools.downloadpage(host, use_cache=True).data
    
    data = scrapertools.find_single_match(data, '<nav class="genres">(.*?)</nav>')
    data = re.sub("<ul class='children'>.*?</ul>", '', data) # quitar subgéneros
    
    matches = scrapertools.find_multiple_matches(data, '<a href="([^"]+)"[^>]*>([^<]+)</a>\s*<i>([0-9.]+)</i>')
    for url, title, num in matches:
        if title.startswith('Años') or title.startswith('Siglo'): continue
        if 'genre/1001-peliculas-que-ver/' in url: continue
        if num == '0': continue
        if descartar_xxx and scrapertools.es_genero_xxx(title): continue

        itemlist.append(item.clone( action='list_all', title='%s (%s)' % (title, num), url=url ))

    return itemlist

def subgeneros(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)
    
    data = httptools.downloadpage(host, use_cache=True).data
    
    data = scrapertools.find_single_match(data, '<nav class="genres">(.*?)</nav>')
    
    matches1 = scrapertools.find_multiple_matches(data, '<a href="[^"]+"[^>]*>([^<]+)</a>\s*<i>[0-9.]+</i><ul class=\'children\'>(.*?)</ul>')
    for padre, hijos in matches1:
        matches = scrapertools.find_multiple_matches(hijos, '<a href="([^"]+)"[^>]*>([^<]+)</a>\s*<i>([0-9.]+)</i>')
        for url, title, num in matches:
            if num == '0': continue
            if descartar_xxx and scrapertools.es_genero_xxx(title): continue
            itemlist.append(item.clone( action='list_all', title='%s / %s (%s)' % (padre, title, num), url=url ))

    return itemlist

def epocas(item):
    logger.info()
    itemlist = []
    
    data = httptools.downloadpage(host, use_cache=True).data
    
    data = scrapertools.find_single_match(data, '<nav class="genres">(.*?)</nav>')
    
    matches = scrapertools.find_multiple_matches(data, '<a href="([^"]+)"[^>]*>((?:Años|Siglo)[^<]+)</a>\s*<i>([0-9.]+)</i>')
    for url, title, num in matches:
        if num == '0': continue
        aux = title.replace('Años ','').replace('Siglo ','')
        itemlist.append(item.clone( action='list_all', title='%s (%s)' % (title, num), url=url, aux=aux ))

    orden = ['10','20','30','40','50','60','70','80','90','1800','1900','2000','X','XI','XII','XIII','XIV','XV','XVI','XVII','XVIII','XIX','XX']
    return sorted(itemlist, key=lambda it: orden.index(it.aux) if it.aux in orden else 999)

def anios(item):
    logger.info()
    itemlist = []
    
    data = httptools.downloadpage(host, use_cache=True).data
    
    data = scrapertools.find_single_match(data, '<ul class="releases scrolling">(.*?)</ul>')
    
    matches = scrapertools.find_multiple_matches(data, '<a href="([^"]+)"[^>]*>([^<]+)</a>')
    for url, title in matches:
        itemlist.append(item.clone( action='list_all', title=title, url=url ))

    for ano in range(1969, 1908, -1):
        itemlist.append(item.clone( action = 'list_all', title = str(ano), url = host + 'release/' + str(ano) + '/' ))

    return itemlist

def directores(item):
    logger.info()
    itemlist = []
    
    data = httptools.downloadpage(host, use_cache=True).data
    
    bloque = scrapertools.find_single_match(data, '<h2 class="widget-title">Directores destacados</h2><div class="tagcloud">(.*?)</div>')
    
    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)".*?aria-label="([^"]+)')
    for url, title in matches:
        num = scrapertools.find_single_match(title, '\((\d+) elementos\)')
        title = title.replace('(%s elementos)' % num, '')

        itemlist.append(item.clone( action='list_all', title='%s (%s)' % (title, num), url=url ))

    # ~ return sorted(itemlist, key=lambda it: it.title)
    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        title = scrapertools.find_single_match(article, ' alt="([^"]+)"')
        if not url or not title: continue
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        year = scrapertools.find_single_match(article, '<span>(\d{4})</span>')
        if not year: year = scrapertools.find_single_match(article, ' (\d{4})</span>')
        if not year: year = '-'
        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<div class="texto">(.*?)</div>'))
        langs = set(scrapertools.find_multiple_matches(article, 'flags/([^.]+)'))
        
        title = title.replace('&#8211;', '-')
        title_alt = title.split(' -')[0].strip() if ' -' in title else '' # para mejorar detección en tmdb
        if not title_alt: title_alt = title.split(' (')[0].strip() if ' (' in title else '' # para mejorar detección en tmdb

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, 
                                    # ~ languages=','.join([IDIOMAS.get(lang, lang) for lang in langs]),
                                    languages=','.join(langs),
                                    contentType='movie', contentTitle=title, contentTitleAlt = title_alt, 
                                    infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    next_page = scrapertools.find_single_match(data, '<a href="([^"]+)"[^>]*><span class="icon-chevron-right"')
    if next_page:
       itemlist.append(item.clone (url = next_page, page = 0, title = '>> Página siguiente', action = 'list_all'))

    return itemlist



#Extraer enlaces de <iframe src="... y <source type="video/mp4" src="...
def extraer_embeds(data):
    itemlist = []

    for tipo in ['iframe', 'source']:
        matches = scrapertools.find_multiple_matches(data, '<%s.*? src="([^"]+)' % tipo)
        for url in matches:
            if 'facebook.com' in url or 'twitter.com' in url or 'google.com' in url: continue
            if url.startswith('//'): url = 'https:' + url
            if '.us.archive.org' in url: servidor = 'directo'
            else: 
                servidor = servertools.get_server_from_url(url)
                if not servidor or servidor == 'directo': continue
                url = servertools.normalize_url(servidor, url)

            itemlist.append(Item( channel = 'zoowoman', action = 'play', server = servidor, language = '?',
                                  title = '', url = url, other = 'iframe/source' ))

    return itemlist

def corregir_servidor(servidor):
    servidor = servertools.corregir_servidor(servidor)
    return servidor

def findvideos(item):
    logger.info()
    itemlist = []
    
    data = httptools.downloadpage(item.url).data
    # ~ logger.debug(data)

    # Embeds
    matches = scrapertools.find_multiple_matches(data, '<li><a class="options" href="#(option-\d+)"(.*?)</li>')
    for opt, resto in matches:
        url = scrapertools.find_single_match(data, '<div id="%s".*? src="([^"]+)' % opt)
        if not url: continue
        
        lang = scrapertools.find_single_match(resto, 'img/flags/([^.]+)')
        if not lang: lang = '?'

        if '.us.archive.org' in url: servidor = 'directo'
        else:
            servidor = servertools.get_server_from_url(url)
            if not servidor or servidor == 'directo': continue
            url = servertools.normalize_url(servidor, url)

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, 
                              title = '', url = url,
                              language = IDIOMAS.get(lang,'VO'), other = lang if lang != '?' else ''
                       ))

    # iframe / sources
    if len(itemlist) == 0:
        itemlist.extend(extraer_embeds(data))

    # Ver en línea / descargas
    for tipo in ['views', 'downloads']:
        bloque = scrapertools.find_single_match(data, '<div id="%s"(.*?)</table>' % tipo)

        matches = scrapertools.find_multiple_matches(bloque, '<tr id="[^"]+">(.*?)</tr>')
        for enlace in matches:
            url = scrapertools.find_single_match(enlace, ' href="([^"]+)')
            if not url: continue
            tds = scrapertools.find_multiple_matches(enlace, '<td[^>]*>(.*?)</td>')

            if 'torrent' in tds[4].lower():
                servidor = 'torrent'
            else:
                servidor = corregir_servidor(scrapertools.find_single_match(enlace, "domain=([^.'\"]+)"))
            if not servidor or servidor == 'zoowoman': continue

            qlty = tds[2]
            lang = tds[3].lower()
            other = 'hace ' + (tds[5] if tipo == 'downloads' else tds[4])
            
            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, 
                                  title = '', url = url,
                                  language = IDIOMAS.get(lang,lang), other = other
                           ))

    return itemlist

def play(item):
    logger.info()
    itemlist = []

    if host in item.url:
        data = httptools.downloadpage(item.url).data
        # ~ logger.debug(data)
        url = scrapertools.find_single_match(data, "window.location.href='([^']+)")
        if url: 
            # ~ logger.info(url)
            if item.server == 'torrent': servidor = 'torrent'
            elif '.us.archive.org' in url: servidor = 'directo'
            else: 
                servidor = servertools.get_server_from_url(url)
                if not servidor or servidor == 'directo': return itemlist
                url = servertools.normalize_url(servidor, url)
            itemlist.append(item.clone( url=url, server=servidor ))
    else:
        itemlist.append(item.clone())

    return itemlist



def list_search(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<div class="result-item">(.*?)</article>')

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        title = scrapertools.find_single_match(article, ' alt="([^"]+)"')
        if not url or not title: continue

        year = scrapertools.find_single_match(article, '<span class="year">(\d+)</span>')
        if not year: year = scrapertools.find_single_match(article, '<span>(\d{4})</span>')
        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<p>(.*?)</p>'))
        langs = set(scrapertools.find_multiple_matches(article, 'flags/([^.]+)'))
        
        title = title.replace('&#8211;', '-')
        title_alt = title.split(' -')[0].strip() if ' -' in title else '' # para mejorar detección en tmdb
        if not title_alt: title_alt = title.split(' (')[0].strip() if ' (' in title else '' # para mejorar detección en tmdb
        
        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, 
                                    languages=','.join(langs),
                                    contentType='movie', contentTitle=title, contentTitleAlt = title_alt, 
                                    infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    next_page = scrapertools.find_single_match(data, '<a href="([^"]+)"[^>]*><span class="icon-chevron-right">')
    if next_page:
       itemlist.append(item.clone (url = next_page, page = 0, title = '>> Página siguiente', action = 'list_search'))

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
