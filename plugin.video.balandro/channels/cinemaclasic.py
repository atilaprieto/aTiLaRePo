# -*- coding: utf-8 -*-

import re

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools

host = 'https://cinemaclasic.atwebpages.com/'

perpage = 25 # preferiblemente un múltiplo de los elementos que salen en la web (5x10=50) para que la subpaginación interna no se descompense

def mainlist(item):
    return mainlist_pelis(item)

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Últimas películas', action = 'list_all', url = host + 'pelicula/' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone ( title = 'Por año', action = 'anios', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Por directores/directoras', action = 'directores_actores', tipo = 'directores' ))
    itemlist.append(item.clone ( title = 'Por actores/actrices', action = 'directores_actores', tipo = 'actores' ))

    itemlist.append(item.clone ( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []
    
    data = httptools.downloadpage(host).data
    
    bloque = scrapertools.find_single_match(data, '<ul id="menu-generos" class="menu">(.*?)</ul>')
    
    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)"[^>]*>([^<]+)')
    for url, title in matches:
        itemlist.append(item.clone( action='list_all', title=title, url=url ))

    itemlist.append(item.clone( action = 'list_all', title = 'Animación', url = host + 'genero/animacion/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Ciencia ficción', url = host + 'genero/ciencia-ficcion/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Documental', url = host + 'genero/documental/' ))

    return sorted(itemlist, key=lambda it: it.title)

def anios(item):
    logger.info()
    itemlist = []
    
    data = httptools.downloadpage(host).data
    
    bloque = scrapertools.find_single_match(data, '<ul class="releases scrolling">(.*?)</ul>')
    
    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)"[^>]*>([^<]+)</a>')
    for url, title in matches:
        itemlist.append(item.clone( action='list_all', title=title, url=url ))

    for ano in range(1967, 1914, -1):
        itemlist.append(item.clone( action = 'list_all', title = str(ano), url = host + 'ano/' + str(ano) + '/' ))

    return itemlist

def directores_actores(item):
    logger.info()
    itemlist = []
    
    data = httptools.downloadpage(host).data
    
    tipo = 'DIRIGIDAS POR' if item.tipo == 'directores' else 'ACTORES/ACTRICES'
    bloque = scrapertools.find_single_match(data, '<h2 class="widget-title">%s(.*?)</div>' % tipo)
    
    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)"[^>]*>([^<]+)<span class="tag-link-count"> \((\d+)\)')
    for url, title, num in matches:
        itemlist.append(item.clone( action='list_all', title='%s (%s)' % (title, num), url=url ))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data
    if '<h1>Películas' in data: data = data.split('<h1>Películas')[1] # descartar lista de destacadas
    if '<div class="sidebar' in data: data = data.split('<div class="sidebar')[0] # descartar listas laterales
    # ~ logger.debug(data)

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)
    num_matches = len(matches)

    for article in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        title = scrapertools.find_single_match(article, '<h4>(.*?)</h4>')
        if not title: title = scrapertools.find_single_match(article, ' alt="([^"]+)"')
        if not url or not title: continue
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        year = scrapertools.find_single_match(article, '<span>(\d{4})</span>')
        if not year: year = scrapertools.find_single_match(article, ' (\d{4})</span>')
        if not year: year = '-'
        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<div class="texto">(.*?)</div>'))
        plot = re.sub('^Impactos: \d+', '', plot)
        
        title = title.replace('&#8211;', '-')
        if '-' in title: title = title.split('-')[0].strip() # Dos cabalgan juntos- John Ford
        if year and year in title: title = title.replace(year, '').strip() # The Doorway to Hell (La senda del crimen) 1930
        title_alt = title.split(' (')[0].strip() if ' (' in title else '' # para mejorar detección en tmdb

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, 
                                    contentType='movie', contentTitle=title, contentTitleAlt = title_alt, 
                                    infoLabels={'year': year, 'plot': plot} ))

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
        next_page = scrapertools.find_single_match(data, '<a href="([^"]+)"[^>]*><span class="icon-chevron-right">')
        if next_page:
           itemlist.append(item.clone (url = next_page, page = 0, title = '>> Página siguiente', action = 'list_all'))

    return itemlist


def extraer_mycinedesiempre(data):
    itemlist = []
    bloque = scrapertools.find_single_match(data, "<div class='post bar hentry'>(.*?)<strong>Share this article</strong>")

    # Enlaces
    matches = scrapertools.find_multiple_matches(bloque, ' href="([^"]+)[^>]*>(.*?)</a>')
    for url, txt in matches:
        if url.startswith('/') or 'filmaffinity.com' in url or 'blogspot.com' in url: continue
        if 'facebook.com' in url or 'twitter.com' in url or 'google.com' in url: continue
        if 'film/reviews/' in url or 'filmreviews/' in url: continue
        # ~ logger.info('%s %s' % (url, txt))
        
        txt = txt.lower()
        if 'vose' in txt or 'v.o.s.e' in txt: lang = 'VOSE'
        elif 'castellano' in txt: lang = 'Esp'
        else: lang = ''
        
        if '.us.archive.org' in url: servidor = 'directo'
        else: servidor = ''

        itemlist.append(Item( channel = 'cinemaclasic', action = 'play', server = servidor, 
                              title = '', url = url, language = lang ))

    # Embeds
    itemlist.extend(extraer_embeds(bloque))

    return itemlist

#Extraer enlaces de <iframe src="... y <source type="video/mp4" src="...
def extraer_embeds(data):
    itemlist = []

    for tipo in ['iframe', 'source']:
        matches = scrapertools.find_multiple_matches(data, '<%s.*? src="([^"]+)' % tipo)
        for url in matches:
            if 'facebook.com' in url or 'twitter.com' in url or 'google.com' in url: continue
            if '.us.archive.org' in url: servidor = 'directo'
            elif 'archive.org' in url: servidor = 'archiveorg'
            elif 'mail.ru' in url: servidor = 'mailru'
            elif 'youtube.com' in url: servidor = 'youtube'
            else: servidor = ''

            if url.startswith('//'): url = 'https:' + url
            itemlist.append(Item( channel = 'cinemaclasic', action = 'play', server = servidor, 
                                  title = '', url = url ))

    return itemlist

def corregir_servidor(servidor):
    servidor = servertools.corregir_servidor(servidor)
    return servidor

def findvideos(item):
    logger.info()
    itemlist = []
    
    IDIOMAS = {'spanish':'Esp', 'vose':'VOSE'}

    data = httptools.downloadpage(item.url).data
    # ~ logger.debug(data)

    # Ver en línea / descargas
    done_mycinedesiempre = False
    for tipo in ['videos', 'download']:
        bloque = scrapertools.find_single_match(data, "<div id='%s'(.*?)</table>" % tipo)
        # ~ logger.debug(bloque)

        matches = scrapertools.find_multiple_matches(bloque, "<tr id='link-[^']+'>(.*?)</tr>")
        for enlace in matches:
            # ~ logger.debug(enlace)

            url = scrapertools.find_single_match(enlace, " href='([^']+)")
            if not url: continue
            if '.us.archive.org' in enlace: servidor = 'directo'
            elif 'archive.org' in enlace: servidor = 'archiveorg'
            else:
                servidor = corregir_servidor(scrapertools.find_single_match(enlace, "domain=([^'.]+)"))
            if not servidor: continue

            if servidor == 'mycinedesiempre':
                if done_mycinedesiempre: continue # No repetir acceso a mycinedesiempre
                data2 = httptools.downloadpage(url).data
                url = scrapertools.find_single_match(data2, '<a id="link" rel="nofollow" href="([^"]+)')
                if url:
                    done_mycinedesiempre = True
                    data2 = httptools.downloadpage(url).data
                    itemlist.extend(extraer_mycinedesiempre(data2))
                continue
                
            tds = scrapertools.find_multiple_matches(enlace, '<td>(.*?)</td>')
            lang = tds[1].lower()
            other = 'hace ' + tds[3]
            # ~ other += ', ' + tipo

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, 
                                  title = '', url = url,
                                  language = IDIOMAS.get(lang,lang), other = other
                           ))

    # Embeds (iframes / sources)
    itemlist.extend(extraer_embeds(data))

    # Obtener servers pendientes de asignar
    if len(itemlist) > 0: itemlist = servertools.get_servers_itemlist(itemlist)

    # Descartar enlaces de youtube (coloquios, trailers, ...) y vsmobi, embedy (pq suelen fallar) a menos que no haya otros enlaces
    # tb videos (videos.2000peliculassigloxx.com)
    validos = len([it for it in itemlist if it.server not in ['desconocido', 'youtube', 'vsmobi', 'embedy', 'videos'] and servertools.is_server_enabled(it.server)])
    if validos > 0: itemlist = filter(lambda it: it.server not in ['youtube', 'vsmobi', 'embedy'], itemlist) # mantener desconocido, videos para listarse en servers_todo

    return itemlist

def play(item):
    logger.info()
    itemlist = []

    if host in item.url:
        data = httptools.downloadpage(item.url).data
        # ~ logger.debug(data)
        url = scrapertools.find_single_match(data, '<a id="link" rel="nofollow" href="([^"]+)')
        if url: 
            if 'ok.cinetux.me/player/ok/?v=' in url:
                data = httptools.downloadpage(url).data
                vid = scrapertools.find_single_match(data, ' src=".*?\#([^"]+)')
                if vid: 
                    itemlist.append(item.clone( server = 'okru', url='https://ok.ru/videoembed/' + vid ))
            else:
                itemlist.append(item.clone( url=servertools.normalize_url(item.server, url) ))
    else:
        itemlist.append(item.clone())

    return itemlist



def list_search(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    matches = re.compile('<div class="result-item">(.*?)</article>', re.DOTALL).findall(data)
    num_matches = len(matches)

    for article in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        title = scrapertools.find_single_match(article, ' alt="([^"]+)"')
        if not url or not title: continue

        year = scrapertools.find_single_match(article, '<span class="year">(\d+)</span>')
        if not year: year = scrapertools.find_single_match(article, '<span>(\d{4})</span>')
        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<p>(.*?)</p>'))
        plot = re.sub('^Impactos: \d+', '', plot)
        
        title = title.replace('&#8211;', '-')
        if '-' in title: title = title.split('-')[0].strip() # Dos cabalgan juntos- John Ford
        if year and year in title: title = title.replace(year, '').strip() # The Doorway to Hell (La senda del crimen) 1930
        title_alt = title.split(' (')[0].strip() if ' (' in title else '' # para mejorar detección en tmdb

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, 
                                    contentType='movie', contentTitle=title, contentTitleAlt = title_alt, 
                                    infoLabels={'year': year, 'plot': plot} ))

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
