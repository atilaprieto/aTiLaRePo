# -*- coding: utf-8 -*-
# -*- Channel Club De Cine -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import re

from core import tmdb
from core import httptools
from core.item import Item
from core import servertools
from core import scrapertools
from bs4 import BeautifulSoup
from channelselector import get_thumb
from platformcode import config, logger
from channels import filtertools, autoplay

list_language = list()
list_quality = []
list_servers = ['supervideo', "vidcloud", "myvy"]

host = "https://mycinedesiempre.blogspot.com/"


def mainlist(item):
    logger.info()

    itemlist = list()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, title="Ultimas", url=host, action="list_all",
                         thumbnail=get_thumb('last', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Español", url=host + "search/label/Espa%C3%B1a",
                         action="list_all", thumbnail=get_thumb('españolas', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Latino", url=host + "search/label/Latino", action="list_all",
                         thumbnail=get_thumb('latino', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Asiaticas", url=host + "search/label/Asi%C3%A1tico", action="list_all",
                         thumbnail=get_thumb('asiaticas', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Generos", action="section",
                         thumbnail=get_thumb('genres', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Buscar...",  url=host + 'search?q=',  action="search",
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
    matches = soup.find("div", class_="main section").find_all("div", class_="post bar hentry")

    for elem in matches:
        url = elem.h2.a["href"]
        title = elem.h2.text.split(" - ")[0].strip()
        thumb = elem.img["src"]
        try:
            year = elem.find("dd", itemprop="datePublished").text
        except:
            year = "-"

        itemlist.append(Item(channel=item.channel, title=title, url=url, action='findvideos',
                            thumbnail=thumb, contentTitle=title, infoLabels={'year': year}))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    url_next_page = soup.find("a", class_="blog-pager-older-link")["href"]
    if url_next_page and len(itemlist) > 8:
        itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=url_next_page, action='list_all'))


    return itemlist


def section(item):
    logger.info()

    itemlist = list()
    listed = list()
    soup = create_soup(host)
    if item.title == "Generos":
        matches = soup.find_all("a", href=re.compile(r"%ssearch.*?" % host), rel="tag")
    for elem in matches:
        url = elem["href"]
        title = elem.text
        if url not in listed:
            itemlist.append(Item(channel=item.channel, title=title, action="list_all", url=url))
            listed.append(url)

    return sorted(itemlist, key=lambda x: x.title)


def findvideos(item):
    logger.info()

    itemlist = list()
    soup = create_soup(item.url).find("div", class_="post bar hentry")
    red_links = soup.find_all("a", target="_blank")
    for link in red_links:
        url = link["href"]
        itemlist.append(Item(channel=item.channel, title='%s', action='play', url=url, infoLabels=item.infoLabels))
    try:
        player_src = (soup.find("iframe")["src"])
        itemlist.append(Item(channel=item.channel, title='%s', action='play', url=player_src, infoLabels=item.infoLabels))
    except:
        pass

    itemlist = servertools.get_servers_itemlist(itemlist)

    # Requerido para FilterTools

    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos':
        itemlist.append(Item(channel=item.channel, title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
                             url=item.url, action="add_pelicula_to_library", extra="findvideos",
                             contentTitle=item.contentTitle))

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
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []