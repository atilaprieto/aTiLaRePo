# -*- coding: utf-8 -*-
# -*- Channel AllPeliculas -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import re
import sys
from core.item import Item
from core import httptools
from core import servertools
from core import scrapertools
from core import tmdb
from platformcode import logger
from channelselector import get_thumb
from bs4 import BeautifulSoup
from channels import filtertools
from channels import autoplay


list_language = ["LAT"]

list_quality = []
list_servers = ["streampe", "fembed", "jawcloud"]

host = "https://allpeliculas.la/"


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


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title="Mas Vistas", url=host + "peliculas-populares", action="list_all",
                         thumbnail=get_thumb("more-watched", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Todas", url=host + "peliculas", action="list_all",
                         thumbnail=get_thumb("all", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Generos", url=host + "peliculas", action="section",
                         thumbnail=get_thumb("all", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Buscar...", url=host+ "peliculas/?type=post&search=",
                         action="search", thumbnail=get_thumb("search", auto=True)))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def list_all(item):
    logger.info()

    itemlist = list()
    #for p in range(2):
    soup = create_soup(item.url)
    matches = soup.find("div", class_="container-fluid mt-5 mr-0 px-lg-5")

    for elem in matches.find_all("div", class_="col-xl-3 col-md-6 col-12 mb-4 position-relative movie-item"):
        url = elem.a["href"]
        title = elem.img["alt"]
        thumb = elem.img["src"]
        year = elem.find("div", class_="rounded-10 px-3 py-2 float-right dark-bg font-size-14 text-inversed").text.strip()

        itemlist.append(Item(channel=item.channel, title=title, url=url, action="findvideos", thumbnail=thumb,
                             contentTitle=title, infoLabels={"year": year}))

        # try:
        #     item.url = soup.find("a", class_="next page-numbers")["href"]
        # except:
        #     break

    tmdb.set_infoLabels_itemlist(itemlist, True)

    # Pagination
    try:
        next_page = soup.find("a", class_="next page-numbers")["href"]
        itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=next_page, action='list_all'))
    except:
        pass

    return itemlist


def section(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url).find("div", class_="filter-options-mob")
    matches = soup.find_all("label", class_=re.compile("dropdown-item"))

    for elem in matches:

        value = elem.find("input", class_="filter-radio")["value"]
        title = elem["title"]
        url = "%s?type=post&genres[]=%s&search" % (item.url, value)

        itemlist.append(Item(channel=item.channel, title=title, url=url, action="list_all"))

    return itemlist


def make_link(item, link_data):
    logger.info()
    if link_data.a:
        id = link_data.a["data-id"]
        server = link_data.a["data-server"]
    else:
        id = link_data.span["data-id"]
        server = link_data.span["data-server"]

    url = "%swp-json/get/player?id=%s&server=%s" % (host, id, server)
    new_item = Item(channel=item.channel, title=server.capitalize(), url=url, action="play", server=server.capitalize(),
                    language="LAT", infoLabels=item.infoLabels)

    return new_item


def findvideos(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)
    matches = soup.find("div", class_="episodes-container position-relative")
    if not matches:
        matches = soup.find("div", class_="video-player my-5 my-xl-0")
        new_item = make_link(item, matches)
        if new_item.title.lower() not in ['netu']:
            itemlist.append(new_item)
    else:
        for elem in matches.find_all("li"):
            new_item = make_link(item, elem)
            if new_item.title.lower() not in ['netu']:
                itemlist.append(new_item)

    # Requerido para FilterTools

    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    return itemlist


def play(item):
    logger.info()

    itemlist = list()

    data = httptools.downloadpage(item.url).json
    itemlist.append(item.clone(url=data["embed_player"]))

    servertools.get_servers_itemlist(itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    try:
        texto = texto.replace(" ", "+")
        if texto != '':
            item.url += texto
            return list_all(item)
        else:
            return []
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    try:
        if categoria in ['peliculas','latino']:
            item.url = host + "peliculas"
            itemlist = list_all(item)

            if itemlist[-1].action == "list_all":
                itemlist.pop()
    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []
    return itemlist
