# -*- coding: utf-8 -*-
# -*- Channel Clasico TV-*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

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
import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int


list_language = ["LAT"]

list_quality = []

list_servers = [
    'sendvid',
    ]

host = 'https://clasico.tv/'


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title='Todas', url=host + 'tvshows/', action='list_all',
                         thumbnail=get_thumb('all', auto=True)))

    itemlist.append(Item(channel=item.channel, title='A-Z', action='section',
                         thumbnail=get_thumb('alphabet', auto=True)))

    itemlist.append(
        item.clone(title="Buscar...", action="search", url=host + '?s=', thumbnail=get_thumb("search", auto=True),
                   extra='movie'))

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


def section(item):
    logger.info()
    itemlist = list()

    soup = create_soup(host)

    matches = soup.find("ul", class_="glossary")

    for elem in matches:
        title = elem.a.text
        itemlist.append(Item(channel=item.channel, action="alpha", title=title.upper()))
    return itemlist


def alpha(item):
    logger.info()

    itemlist = []

    url = '%s/wp-json/dooplay/glossary/?term=%s&nonce=262b33c1c6&type=all' % (host, item.title.lower())
    dict_data = httptools.downloadpage(url).json
    if 'error' not in dict_data:
        for elem in dict_data:
            elem = dict_data[elem]
            thumb = re.sub(r'-\d+x\d+.jpg', '.jpg', elem['img'])

            itemlist.append(Item(channel=item.channel, action='seasons', title=elem['title'],
                                 url=elem['url'], thumbnail=thumb, contentSerieName=elem['title']))
    tmdb.set_infoLabels_itemlist(itemlist, True)
    return itemlist


def list_all(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)
    matches = soup.find("div", class_="content").find_all("article", id=re.compile(r"^post-\d+"))

    for elem in matches:

        info_1 = elem.find("div", class_="poster")

        thumb = info_1.img["src"]
        title = info_1.img["alt"]
        title = re.sub(r" \([^)]+\)", "", title)
        url = elem.a["href"]

        itemlist.append(Item(channel=item.channel, title=title, url=url, thumbnail=thumb, contentSerieName=title,
                             action="seasons"))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    try:
        url_next_page = soup.find_all("a", class_="arrow_pag")[-1]["href"]
    except:
        return itemlist

    itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=url_next_page, action='list_all'))

    return itemlist


def seasons(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url).find("div", id="seasons")

    matches = soup.find_all("div", class_="se-c")

    infoLabels = item.infoLabels

    for elem in matches:
        season = elem.find("span", class_="se-t").text
        title = "Temporada %s" % season
        infoLabels["season"] = season

        itemlist.append(Item(channel=item.channel, title=title, url=item.url, action='episodesxseasons',
                             context=filtertools.context(item, list_language, list_quality), infoLabels=infoLabels))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    if config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(
            Item(channel=item.channel, title='[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]', url=item.url,
                 action="add_serie_to_library", extra="episodios", contentSerieName=item.contentSerieName))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []
    templist = seasons(item)
    for tempitem in templist:
        itemlist += episodesxseasons(tempitem)

    return itemlist


def episodesxseasons(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url).find("div", id="seasons")

    matches = soup.find_all("div", class_="se-c")
    infoLabels = item.infoLabels
    season = infoLabels["season"]

    for elem in matches:
        if elem.find("span", class_="se-t").text != str(season):
            continue

        epi_list = elem.find("ul", class_="episodios")
        for epi in epi_list.find_all("li"):
            info = epi.find("div", class_="episodiotitle")
            url = info.a["href"]
            epi_name = info.a.text
            epi_num = epi.find("div", class_="numerando").text.split(" - ")[1]
            infoLabels["episode"] = epi_num
            title = "%sx%s - %s" % (season, epi_num, epi_name)

            itemlist.append(Item(channel=item.channel, title=title, url=url, action='findvideos',
                                 infoLabels=infoLabels))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)
    matches = soup.find("ul", id="playeroptionsul")

    for elem in matches.find_all("li"):
        if "youtube" in elem.find("span", class_="server").text:
            continue
        post = {"action": "doo_player_ajax", "post": elem["data-post"], "nume": elem["data-nume"],
                "type": elem["data-type"]}
        headers = {"Referer": item.url}
        doo_url = "%swp-admin/admin-ajax.php" % host
        data = httptools.downloadpage(doo_url, post=post, headers=headers).json
        try:
            url = BeautifulSoup(data.get("embed_url", ""), "html5lib").find("iframe")["src"]
        except:
            continue

        if not url.startswith("http"):
            url = "https:%s" % url
        itemlist.append(Item(channel=item.channel, title="%s", action="play", url=url,
                             language="LAT", infoLabels=item.infoLabels))

    itemlist = servertools.get_servers_itemlist(itemlist, lambda x: x.title % x.server.capitalize())

    # Requerido para FilterTools

    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)
    if item.contentType != "episode":
        if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != "findvideos":
            itemlist.append(Item(channel=item.channel, title="[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]",
                                 url=item.url, action="add_pelicula_to_library", extra="findvideos",
                                 contentTitle=item.contentTitle))

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
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def search_results(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)

    for elem in soup.find_all("div", class_="result-item"):

        url = elem.a["href"]
        thumb = elem.img["src"]
        title = elem.img["alt"]
        year = elem.find("span", class_="year").text

        language = "LAT"

        new_item = Item(channel=item.channel, title=title, url=url, thumbnail=thumb,
                        language=language, infoLabels={'year': year})

        if "movies" in url:
            new_item.action = "findvideos"
            new_item.contentTitle = new_item.title
        else:
            new_item.action = "seasons"
            new_item.contentSerieName = new_item.title
            new_item.context = filtertools.context(item, list_language, list_quality)

        itemlist.append(new_item)

    tmdb.set_infoLabels_itemlist(itemlist, True)

    try:
        url_next_page = soup.find_all("a", class_="arrow_pag")[-1]["href"]
    except:
        return itemlist

    itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=url_next_page, action='search_results'))

    return itemlist
