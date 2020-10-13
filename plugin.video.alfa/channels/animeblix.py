# -*- coding: utf-8 -*-
# -*- Channel Animeblix -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

from bs4 import BeautifulSoup
from channelselector import get_thumb
from core import httptools
from core import scrapertools
from core import servertools
from core.item import Item
from platformcode import config, logger
from channels import filtertools, autoplay
from core import tmdb
from core import jsontools


IDIOMAS = {"latino": "LAT", "castellano": "CAST"}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['directo', 'fembed', 'streamtape']

host = "https://animeblix.com/"

def mainlist(item):
    logger.info()

    itemlist = list()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, title="Nuevos Capítulos", url=host, action="new_episodes",
                         thumbnail=get_thumb('new episodes', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Anime", action="sub_menu",
                         thumbnail=get_thumb('anime', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Películas", url=host + 'animes', action="list_all",
                         s_type="search?type=MOVIE", thumbnail=get_thumb('movies', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Buscar", url=host + 'animes', action="search",
                         thumbnail=get_thumb('search', auto=True)))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def sub_menu(item):
    logger.info()

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title="Ultimos", url=host + 'animes', action="list_all",
                         s_type="search?type=TV&is_completed=0", thumbnail=get_thumb('all', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Todos", url=host + 'animes', action="list_all",
                         s_type="search?type=TV", thumbnail=get_thumb('all', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Castellano", url=host + 'animes', action="list_all",
                         s_type="search?language=CASTELLANO&type=TV", thumbnail=get_thumb('cast', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Latino", url=host + 'animes', action="list_all",
                         s_type="search?language=LATINO&type=TV", thumbnail=get_thumb('latino', auto=True)))

    return itemlist

def create_soup(url, referer=None, unescape=False):
    logger.info()

    if referer:
        data = httptools.downloadpage(url, headers={'Referer':referer}).data
    else:
        data = httptools.downloadpage(url).data

    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")

    return soup


def new_episodes(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url).find("section", class_="latest-episodes")
    matches = soup.find("div", class_="row mx-n2").find_all("article", class_="card")

    for elem in matches:
        title = elem.img["alt"]
        thumb = elem.img["data-src"]
        url = elem.a["href"]
        itemlist.append(Item(channel=item.channel, title=title, thumbnail=thumb, url=url, action="findvideos"))

    return itemlist


def episodios(item):
    logger.info()

    itemlist = list()

    data = httptools.downloadpage(item.url).data
    matches = scrapertools.find_single_match(data, 'episodes="([^"]+)')
    matches = jsontools.load(scrapertools.unescape(matches))
    infoLabels = item.infoLabels

    for elem in matches["data"]:
        url = "%s%s-%s-%s" % (host, elem["anime"]["slug"], elem["number"], elem["uuid"])
        uuid = elem["uuid"]
        title = "1x%s - Episodio %s" % (elem["number"], elem["number"])
        epi_num = elem["number"]
        infoLabels['season'] = '1'
        infoLabels['episode'] = epi_num
        itemlist.append(Item(channel=item.channel, title=title, url=url, uuid=uuid, action='findvideos',
                             language=item.language, infoLabels=infoLabels))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    itemlist = itemlist[::-1]

    if config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(
            Item(channel=item.channel, title='[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]', url=item.url,
                 action="add_serie_to_library", extra="episodios", contentSerieName=item.contentSerieName,
                 extra1='library'))

    return itemlist


def list_all(item):
    logger.info()

    itemlist = list()
    base_url = "%s/%s" % (item.url, item.s_type)
    headers = {"referer": item.url, "x-requested-with": "XMLHttpRequest"}
    matches = httptools.downloadpage(base_url, headers=headers).json

    for elem in matches["data"]:
        url = elem["url"]
        title = elem["title"]
        lang = "VOSE"
        if "latino" in title.lower():
            title = title.replace(" Latino", "")
            lang = "LAT"
        elif "castellano" in title.lower():
            title = title.replace(" Castellano", "")
            lang = "CAST"
        thumb = host + elem["imgPortait"]
        plot = elem["synopsis"]

        new_item = Item(channel=item.channel, title=title, url=url, action='episodios', plot=plot,
                        thumbnail=thumb, language=lang, infoLabels={"year": "-"})

        if "MOVIE" in base_url:
            new_item.contentTitle = title
        else:
            new_item.contentSerieName = title

        itemlist.append(new_item)


    tmdb.set_infoLabels_itemlist(itemlist, True)

    next = int(matches["meta"]["current_page"]) + 1
    if next <= matches["meta"]["last_page"]:
        s_type = "%s&page=%s" % (item.s_type, next)
        itemlist.append(item.clone(title="Siguiente >>", s_type=s_type))

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()
    if item.uuid:
        ref = item.url
    else:
        item.uuid = scrapertools.find_single_match(item.url, "\d+-(.+)")
        ref = host
    base_url = "%sepisodes/player-options/%s" % (host, item.uuid)
    headers = {"referer": ref, "x-requested-with": "XMLHttpRequest"}
    urls = httptools.downloadpage(base_url, headers=headers).json

    for url in urls:
        url = url["code"]
        if "/stream/" in url:
            data = httptools.downloadpage(url, headers={'Referer': item.url}).data
            url = scrapertools.find_single_match(data, 'file: "([^"]+)"')

        itemlist.append(Item(channel=item.channel, title='%s', action='play', url=url, language=item.language,
                             infoLabels=item.infoLabels))

    itemlist = servertools.get_servers_itemlist(itemlist, lambda x: x.title % x.server.capitalize())

    # Requerido para FilterTools

    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    return itemlist


def search(item, texto):
    logger.info()
    try:
        texto = texto.replace(" ", "+")
        if texto != '':
            item.s_type = "search?nombre=%s" % texto
            return list_all(item)
        else:
            return []
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def newest(categoria):
    itemlist = []
    item = Item()
    if categoria == 'anime':
        item.url=host
        itemlist = new_episodes(item)
    return itemlist
