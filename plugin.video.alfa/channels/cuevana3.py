# -*- coding: utf-8 -*-
# -*- Channel Cuevana 3 -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urllib                                               # Es muy lento en PY2.  En PY3 es nativo
else:
    import urllib                                                               # Usamos el nativo de PY2 que es más rápido

import re

from channelselector import get_thumb
from core import httptools
from core import scrapertools
from core import servertools
from core import tmdb, jsontools
from core.item import Item
from platformcode import config, logger
from channels import autoplay
from channels import filtertools
from bs4 import BeautifulSoup


host = 'https://cuevana3.io/'


IDIOMAS = {"optl": "LAT", "opte": "CAST", "opts": "VOSE"}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['fastplay', 'directo', 'streamplay', 'flashx', 'streamito', 'streamango', 'vidoza']


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title="Todas", action="list_all", url=host+'peliculas',
                         thumbnail=get_thumb('all', auto=True)))
    itemlist.append(Item(channel=item.channel, title="Estrenos", action="list_all", url=host+'estrenos',
                         thumbnail=get_thumb('premieres', auto=True)))
    itemlist.append(Item(channel=item.channel, title="Mas vistas", action="list_all", url=host+'peliculas-mas-vistas',
                         thumbnail=get_thumb('more watched', auto=True)))
    itemlist.append(Item(channel=item.channel, title="Mas votadas", action="list_all", url=host+'peliculas-mas-valoradas',
                         thumbnail=get_thumb('more voted', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Generos", action="genres", section='genre',
                         thumbnail=get_thumb('genres', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Castellano", action="list_all", url= host+'peliculas-espanol',
                         thumbnail=get_thumb('audio', auto=True)))
    
    itemlist.append(Item(channel=item.channel, title="Latino", action="list_all", url=host + 'peliculas-latino',
                         thumbnail=get_thumb('audio', auto=True)))
    
    itemlist.append(Item(channel=item.channel, title="VOSE", action="list_all", url=host + 'peliculas-subtituladas',
                         thumbnail=get_thumb('audio', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=host+'?s=',
                         thumbnail=get_thumb('search', auto=True)))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def create_soup(url, referer=None, unescape=False):
    logger.info()

    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}).data
    else:
        data = httptools.downloadpage(url).data

    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")

    return soup


def list_all(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)

    matches = soup.find("ul", class_="MovieList").find_all("li", class_="xxx")

    for elem in matches:
        thumb = elem.find("figure").img["src"]
        title = elem.find("h2", class_="Title").text
        url = elem.a["href"]
        year = elem.find("span", class_="Year").text

        itemlist.append(Item(channel=item.channel, title=title, url=url, action='findvideos',
                             thumbnail=thumb, contentTitle=title, infoLabels={'year': year}))

    tmdb.set_infoLabels_itemlist(itemlist, True)
    try:
        url_next_page = soup.find("a", class_="next")["href"]
        itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=url_next_page, action='list_all',
                             section=item.section))
    except:
        pass

    return itemlist


def genres(item):
    logger.info()
    itemlist = list()

    soup = create_soup(host)

    action = 'list_all'

    matches = soup.find("li", id="menu-item-1953").find_all("li")

    for elem in matches:
        url = elem.a["href"]
        title = elem.a.text
        if title != 'Ver más':
            new_item = Item(channel=item.channel, title= title, url=url, action=action, section=item.section)
            itemlist.append(new_item)

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list ()

    soup = create_soup(item.url).find("div", class_="TPlayer embed_div")

    matches = soup.find_all("div", class_="TPlayerTb")

    for elem in matches:
        lang = IDIOMAS.get(elem["id"][:-1].lower(), "VOSE")
        elem = elem.find("iframe")
        url = elem["data-src"]

        id = scrapertools.find_single_match(url, '\?h=(.*)')
        logger.error(url)

        if 'cuevana3.io' in url:
            base_url = "https://api.cuevana3.io/ir/rd.php"
            param = 'url'
            
            if '/sc/' in url:
                base_url = "https://api.cuevana3.io/sc/r.php"
                param = 'h'
            

            url = httptools.downloadpage(base_url, post={param: id},
                                        follow_redirects=False).headers.get('location', '')

        if url:
            itemlist.append(Item(channel=item.channel, title="%s", url=url, action="play", language=lang))

    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % '%s [%s]' % (i.server.capitalize(),
                                                                                           i.language))


    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos':
        itemlist.append(
            Item(channel=item.channel, title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]', url=item.url,
                 action="add_pelicula_to_library", extra="findvideos", contentTitle=item.contentTitle))

    return itemlist


def search(item, texto):
    logger.info()

    try:
        texto = texto.replace(" ", "+")
        item.url = item.url + texto

        if texto != '':
            return list_all(item)
        else:
            return []
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys

        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    try:
        if categoria == 'infantiles':
            item.url = host+'/category/animacion'
        elif categoria == 'terror':
            item.url = host+'/category/terror'
        elif categoria == 'documentales':
            item.url = host+'/category/documental'
        itemlist = list_all(item)
        if itemlist[-1].title == 'Siguiente >>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist

def play(item):

    if "damedamehoy" in item.url:
        v_data = httptools.downloadpage(item.url).data
        new_url = scrapertools.find_single_match(v_data, "checkUrl = '([^']+)'")
        v_data = httptools.downloadpage(new_url).json
        item.url = v_data["file"]

    return [item]

