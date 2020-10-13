# -*- coding: utf-8 -*-
# -*- Channel EntrePeliculasySeries -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

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

host = 'https://www.entrepeliculasyseries.com/'

IDIOMAS = {"lat": "LAT", "cas": "CAST", "sub": "VOSE", "esp": "CAST"}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['mega', 'fembed', 'vidtodo', 'gvideo']


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title="Peliculas",  action="sub_menu",
                         thumbnail=get_thumb('movies', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Series", action="sub_menu",
                         thumbnail=get_thumb('tvshows', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=host + '?s=',
                         thumbnail=get_thumb('search', auto=True)))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def sub_menu(item):
    logger.info()

    itemlist = list()

    if item.title == "Peliculas":
        itemlist.append(Item(channel=item.channel, title="Todas", action="list_all", url=host + 'ver-peliculas-online',
                             thumbnail=get_thumb('all', auto=True)))

        itemlist.append(Item(channel=item.channel, title="Generos", action="genres", section='genre',
                             thumbnail=get_thumb('genres', auto=True)))
    else:
        itemlist.append(Item(channel=item.channel, title="Ultimas", action="list_all", url=host + 'series-recientes',
                             thumbnail=get_thumb('last', auto=True)))

        itemlist.append(Item(channel=item.channel, title="Todas", action="list_all", url=host + 'ver-series-online',
                             thumbnail=get_thumb('all', auto=True)))

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
    matches = soup.find("div", class_="homecontent")

    for elem in matches.find_all("div", class_="publications-content"):
        url = elem.a["href"]
        fulltitle = elem.h3.text
        year = '-'
        if re.search(r"\(\d+\)", fulltitle):
            title = scrapertools.find_single_match(fulltitle, r"(.*?) \(\d+").strip()
            year = scrapertools.find_single_match(fulltitle, r"\((\d{4})\)")
        else:
            title = fulltitle
        thumb = elem.img["src"]
        new_item = Item(channel=item.channel, title=title, url=url, thumbnail=thumb, infoLabels={'year': year})

        if "/serie" in url:
            new_item.contentSerieName = title
            new_item.action = "seasons"
        else:
            new_item.contentTitle = title
            new_item.action = "findvideos"

        itemlist.append(new_item)

    tmdb.set_infoLabels_itemlist(itemlist, True)

    try:
        url_next_page = soup.find("a", class_="nextpostslink")["href"]

        if url_next_page:
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

    matches = soup.find("li", class_="dropdown-submenu").find_all("li")
    for elem in matches:
        url = elem.a["href"]
        title = elem.a.text
        itemlist.append(Item(channel=item.channel, title=title, url=url, action=action, section=item.section))

    return itemlist


def seasons(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)
    matches = soup.find_all("div", class_="season")
    infoLabels = item.infoLabels

    for elem in matches:
        s_data = elem.h2.text
        title = scrapertools.find_single_match(elem.h2.text, "(Temporada \d+)")
        season = scrapertools.find_single_match(title, "(\d+)")
        infoLabels["season"] = season
        itemlist.append(Item(channel=item.channel, title=title, url=item.url, action='episodesxseason', s_data=s_data,
                             infoLabels=infoLabels))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    if config.get_videolibrary_support() and len(itemlist) > 0 and not item.extra:
        itemlist.append(Item(channel=item.channel,
                             title='[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]',
                             url=item.url,
                             action="add_serie_to_library",
                             extra="episodios",
                             contentSerieName=item.contentSerieName
                             ))

    return itemlist


def episodios(item):
    logger.info()

    itemlist = list()
    templist = seasons(item)
    for tempitem in templist:
        itemlist += episodesxseason(tempitem)

    return itemlist


def episodesxseason(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)
    matches = soup.find_all("div", class_="season")
    infoLabels = item.infoLabels

    for block in matches:

        if block.h2.text != item.s_data:
            continue
        else:
            epis = block.find_all("li")
            for elem in epis:
                try:
                    url = elem.a["href"]
                except:
                    continue
                episode = scrapertools.find_single_match(elem.a.text, r"(\d+)")
                title = "%sx%s" % (infoLabels["season"], episode)
                infoLabels["episode"] = episode

                itemlist.append(Item(channel=item.channel, title=title, url=url, action="findvideos",
                                     infoLabels=infoLabels))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)

    matches = soup.find_all("div", class_=re.compile(r"col-sm-12 col-md-3 option-lang"))
    for elem in matches:

        lang = (elem.find("span", class_="text-options")["id"]).replace("-option", "")

        for opt in elem.find_all("li", class_="option"):
            server = re.sub(opt.find("noscript").text, "", opt.text).strip().lower().replace("| ", "")
            url = opt["data-link"]
            if server == "google drive":
                server = "gvideo"
            if server.lower() in ["descargar"]:
                continue
            itemlist.append(Item(channel=item.channel, title=server.capitalize(), url=url, server=server, action="play",
                                 language=IDIOMAS.get(lang, 'LAT'), infoLabels=item.infoLabels))

    itemlist = sorted(itemlist, key=lambda it: it.language)

    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    if item.contentType == 'movie':
        if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos':
            itemlist.append(
                Item(channel=item.channel, title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
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
        import sys

        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def newest(categoria):
    logger.info()

    item = Item()
    try:
        if categoria == 'peliculas':
            item.url = host + 'ver-peliculas-online'
        elif categoria == 'infantiles':
            item.url = host + 'peliculas-de-animacion'
        elif categoria == 'terror':
            item.url = host + 'peliculas-de-terror'
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
    itemlist = list()

    data = httptools.downloadpage(item.url).data
    url = scrapertools.find_single_match(data, 'window.location="([^"]+)"')
    if not url.startswith("http"):
        url = "https:" + url
    item.server = ""
    itemlist.append(item.clone(url=url))

    itemlist = servertools.get_servers_itemlist(itemlist)
    return itemlist

