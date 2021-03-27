# -*- coding: utf-8 -*-

from platformcode import logger
from core.item import Item
from core import httptools, scrapertools


host = "https://www.area-documental.com/"


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'resultados-reciente.php?buscar=&genero=' ))

    itemlist.append(item.clone( title = 'Destacados', action = 'list_all', url = host + 'resultados.php?buscar=&genero=' ))
    itemlist.append(item.clone( title = 'Más vistos', action = 'list_all', url = host +'resultados-visto.php?buscar=&genero=' ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias' ))
    itemlist.append(item.clone( title = 'Por fecha', action = 'list_all', url = host + 'resultados-anio.php?buscar=&genero=' ))
    itemlist.append(item.clone( title = 'Por alfabético', action = 'list_all', url = host +'resultados-titulo.php?buscar=&genero=' ))

    itemlist.append(item.clone( title = 'En 3D', action = 'list_all', url = host + '3D.php' ))

    itemlist.append(item.clone( title = 'Series', action = 'list_all', url = host + 'series.php' ))

    itemlist.append(item.clone( title = 'Buscar documental ...', action = 'search', search_type = 'documentary' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    patron = '<a href="(resultados[^"]+)" class="dropdown-toggle" data-toggle="dropdown">([^<]+)'
    matches = scrapertools.find_multiple_matches(data, patron)

    for url, title in matches:
        patron = '<li><a href="%s">TODO</a></li>(.*?)</ul>' % url.replace('?', '\?')
        bloque = scrapertools.find_single_match(data, patron)
        subitems = scrapertools.find_multiple_matches(bloque, '<li><a href="[^"]+">([^<]+)')

        itemlist.append(item.clone( action='subcategorias', title=title.strip(), url=host + url, subitems=subitems, plot=', '.join(subitems) ))

    return itemlist

def subcategorias(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='list_all', title='Todo ' + item.title, url=item.url ))

    for subgenero in item.subitems:
        itemlist.append(item.clone( action='list_all', title=subgenero, url=host+'resultados.php?genero=&buscar='+subgenero.replace(' ', '+') ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = '<a class="hvr-shutter-out-horizontal" href="([^"]+)"><img (?:data-|)src="([^"]+)" alt="([^"]+)"'
    patron += '.*?&nbsp;&nbsp;&nbsp;(\d+| ).*?<div class="comments-space">(.*?)</div>'
    matches = scrapertools.find_multiple_matches(data, patron)

    for url, thumb, title, year, plot in matches:
        if 'player.php' not in url:
            titulo = '%s [COLOR gray](%s)[/COLOR]' % (title, year)
            itemlist.append(item.clone( action='list_all', url=url, title=titulo, thumbnail=host+thumb,
                                        plot=scrapertools.htmlclean(plot).strip() ))
        else:
            itemlist.append(item.clone( action='findvideos', url=host+url, title=title, thumbnail=host+thumb,
                                        infoLabels={"year": year, "plot": scrapertools.htmlclean(plot).strip()},
                                        contentType='movie', contentTitle=title, contentExtra='documentary' ))

    next_page_link = scrapertools.find_single_match(data, '<li><a class="last">\d+</a></li>\s*<li>\s*<a href="([^"]+)')
    if next_page_link != '':
        if next_page_link.startswith('?'): 
            if 'series.php' in item.url: next_page_link = host + 'series.php' + next_page_link
            else: next_page_link = host + 'index.php' + next_page_link
        else: next_page_link = host + next_page_link[1:]

        next_page_link = next_page_link.replace('&amp;', '&')
        itemlist.append(item.clone( title='>> Página siguiente', action='list_all', url = next_page_link, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    # ~ logger.debug(data)

    try:
        sub_url, sub_lang = scrapertools.find_single_match(data, 'file:\s*"/(webvtt/[^"]+)",\s*label: "([^"]*)"')
        sub_url = host + sub_url
        sub_url += '|Referer=' + item.url
    except:
        sub_url = ''; sub_lang = ''

    matches = scrapertools.find_multiple_matches(data, 'file:\s*"([^"]+)",.*?label: "([^"]*)"')
    # ~ logger.debug(matches)
    for url, lbl in matches:
        if '.mp4' not in url and url != 'video.php' and url != 'video3Dfull.php': continue
        if url in ['video.php', 'video3Dfull.php']: 
            url = host + url + '|Referer=' + item.url 
            url += '&Cookie=' + httptools.get_cookies('area-documental.com')
        lang = 'Vose' if 'Espa' in sub_lang else 'Esp' # !?

        itemlist.append(Item( channel = item.channel, action = 'play', server='directo', title = '', url = url, 
                              language = lang, quality = lbl, subtitle = sub_url ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'resultados.php?genero=&buscar=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
