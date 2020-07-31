# -*- coding: utf-8 -*-
# -*- Channel CineIS -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

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

host = 'https://cine.is/'

IDIOMAS = {"latino": "LAT", "subtitulado": "VOSE"}
list_language = IDIOMAS.values()
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

    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=host + "results/?type=search&query=",
                         thumbnail=get_thumb('search', auto=True), page=1))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def sub_menu(item):
    logger.info()

    itemlist = list()

    if item.title == "Peliculas":
        itemlist.append(Item(channel=item.channel, title="Todas", action="list_all", url=host + 'results/?cat=1&p=',
                             thumbnail=get_thumb('all', auto=True), page=1))

        itemlist.append(Item(channel=item.channel, title="Generos", action="genres", section='genre',
                             thumbnail=get_thumb('genres', auto=True), cat=1))
    else:
        itemlist.append(Item(channel=item.channel, title="Ultimas", action="list_all", url=host + 'results/?cat=2&p=',
                             thumbnail=get_thumb('last', auto=True), page=1))

        itemlist.append(Item(channel=item.channel, title="Generos", action="genres", section='genre',
                             thumbnail=get_thumb('genres', auto=True), cat=2))

        itemlist.extend(get_platforms(item))

    return itemlist


def get_platforms(item):
    logger.info()

    itemlist = list()

    soup = create_soup(host).find("div", class_="net__row_grid responsive")

    matches = soup.find_all("a")

    for elem in matches:
        title = elem["class"][0]
        title = title.upper() if len(title) < 4 else title.capitalize()
        url = "%sresults/?cat=2&p=&network=%s&p=" % (host, title)
        thumb = host + elem.img["src"]
        itemlist.append(Item(channel=item.channel, title=title, url=url, action="list_all", thumbnail=thumb, page=1))

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
    json_data = {"results": []}
    itemlist = list()
    for x in range(3):
        try:
            matches = httptools.downloadpage('%s%s' % (item.url, item.page)).json
        except:
            break
        if matches and "results" in matches:
            json_data["results"] += matches["results"]
            item.page += 1

    for data in json_data["results"]:
        if "content" in data:
            elem = BeautifulSoup(data["content"], "html5lib", from_encoding="utf-8")
            url = host + elem.a["href"]
            year = scrapertools.find_single_match(data["date"], r"(\d{4})")
        else:
            url = "%s/serie/%s" % (host, data["slug"])
            year = ''
        title = data["titulo"]
        thumb = data["poster"]
        content_id = data["ID"]
        new_item = Item(channel=item.channel, title=title, url=url, thumbnail=thumb, content_id=content_id,
                        infoLabels={'year': year}, info=data)

        if "/serie" in url:
            new_item.contentSerieName = title
            new_item.action = "seasons"
        else:
            new_item.contentTitle = title
            new_item.action = "findvideos"

        itemlist.append(new_item)

    tmdb.set_infoLabels_itemlist(itemlist, True)

    try:
        itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=item.url, action='list_all',
                             page=item.page + 1))
    except:
        pass

    return itemlist


def genres(item):
    logger.info()
    itemlist = list()

    soup = create_soup(host+'peliculas')

    action = 'list_all'
    matches = soup.find("div", id="panel_genres_filter").find_all("a")
    for elem in matches:

        title = elem.text
        url = "%sresults/?cat=%s&genre=%s&p=" % (host, item.cat, title)
        itemlist.append(Item(channel=item.channel, title=title, url=url, action=action, section=item.section, page=0))

    return itemlist


def seasons(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url).find("select")
    matches = soup.find_all("option")
    infoLabels = item.infoLabels

    for elem in matches:
        title = elem.text
        season = scrapertools.find_single_match(title, "(\d+)")
        infoLabels["season"] = season
        itemlist.append(Item(channel=item.channel, title=title, url=item.url, action='episodesxseason',
                             infoLabels=infoLabels, info=item.info))

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
    info = item.info

    url = "%s/ajax/episodios.php?ep=true&se=%s&t=%s&sl=%s" % (host, info["ID"], item.infoLabels["season"], info["titulo"])
    data = httptools.downloadpage(url, headers={"referer": item.url, "x-requested-with": "XMLHttpRequest"}).json
    infoLabels = item.infoLabels
    season = infoLabels["season"]

    for block in data:
        elem = BeautifulSoup(block["contenido"], "html5lib", from_encoding="utf-8")
        url = "%s%s" % (host, elem.a["href"].replace(' ', '-'))
        title = "%sx%s - %s" % (season, block["id"], elem.a.text)
        infoLabels["episode"] = block["id"]

        itemlist.append(Item(channel=item.channel, title=title, url=url, action="findvideos",
                             infoLabels=infoLabels, content_id=block["idep"]))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()
    content_type = "serie" if item.contentType == "episode" else item.contentType

    url = '%s/player/?type=%s&ids=%s&temp=null' % (host, content_type, item.content_id)
    json_data = httptools.downloadpage(url).json

    for srv in json_data:
        lang = srv["idioma"].lower()
        url = scrapertools.find_single_match(srv["enlace"], "id=([^?]+)")
        itemlist.append(Item(channel=item.channel, title='%s', url=url, action="play",
                             language=IDIOMAS.get(lang, 'LAT'), infoLabels=item.infoLabels))

    itemlist = servertools.get_servers_itemlist(itemlist, lambda x: x.title % x.server.capitalize())

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


def search_results(item):
    logger.info()

    itemlist = list()

    json_data = httptools.downloadpage(item.url).json

    for elem in json_data:

        title = elem["titulo"]
        thumb = elem["poster"]
        content_id = elem["ID"]
        new_item = Item(channel=item.channel, title=title, thumbnail=thumb, content_id=content_id, info=elem)

        if elem["type"] == "serie":
            new_item.url = "%s/serie/%s" % (host, elem["slug"])
            new_item.contentSerieName = title
            new_item.action = "seasons"
        else:
            new_item.url = "%s/%s" % (host, elem["slug"])
            new_item.contentTitle = title
            new_item.action = "findvideos"

        itemlist.append(new_item)

    return itemlist


def search(item, texto):
    logger.info()

    try:
        texto = texto.replace(" ", "+")
        item.url = item.url + texto

        if texto != '':
            return search_results(item)
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
            item.url = host + 'results/?cat=1&p='
        elif categoria == 'infantiles':
            item.url = "%sresults/?cat=1&genre=Animación&p=" % host
        elif categoria == 'terror':
            item.url = "%sresults/?cat=1&genre=Terror&p=" % host
        item.page=1
        itemlist = list_all(item)
        if itemlist[-1].title == 'Siguiente >>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


