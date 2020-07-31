# -*- coding: utf-8 -*-
# -*- Channel SerieMega -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-


import re
from channels import filtertools
from bs4 import BeautifulSoup
from core import httptools
from core import scrapertools
from core import servertools
from core.item import Item
from core import tmdb
from channels import autoplay
from platformcode import config, logger
from channelselector import get_thumb
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse

host = 'https://seriemega.net/'
IDIOMAS = {"Latino": "LAT", "Castellano": "CAST", "Subtitulado": "VOSE"}
list_language = IDIOMAS.values()
list_servers = ['directo', 'jawclowd']
list_quality = ['HD-RIP', 'TSC-SCR', 'HD-720', 'HD-1080']


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


def mainlist(item):
    logger.info()

    #autoplay.init(item.channel, list_servers, list_quality)
    itemlist = list()

    itemlist.append(Item(channel=item.channel, title="Peliculas", action="list_all", url=host + "peliculas",
                         thumbnail=get_thumb("movies", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Series", action="list_all", url=host + "serie",
                         thumbnail=get_thumb("tvshows", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Generos", action="section", url=host,
                         thumbnail=get_thumb("genres", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Alfabetico", action="section", url=host,
                         thumbnail=get_thumb("alphabet", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url=host + "?s=",
                         thumbnail=get_thumb("search", auto=True)))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def list_all(item):
    logger.info()

    itemlist = list()
    soup = create_soup(item.url)
    matches = soup.find("ul", class_="MovieList NoLmtxt Rows AX A06 B04 C03 E20")
    if not matches:
        return itemlist

    for elem in matches.find_all("article"):
        url = elem.a["href"]
        title = elem.a.h3.text
        thumb = elem.img
        if thumb.has_attr("data-lazy-src"):
            thumb = thumb["data-lazy-src"]
        else:
            thumb = thumb["src"]
        try:
            year = elem.find("span", class_="Year").text
        except:
            year = '-'
        new_item = Item(channel=item.channel, url=url, title=title, thumbnail=thumb, infoLabels={'year': year})

        if elem.figcaption or elem.find("span", class_="TpTv BgA"):
            new_item.action = "seasons"
            new_item.contentSerieName = title
        else:
            new_item.action = "findvideos"
            new_item.contentTitle = title
        itemlist.append(new_item)

    tmdb.set_infoLabels_itemlist(itemlist, True)
    try:
        next_page = soup.find("a", class_="next page-numbers")["href"]

        itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=next_page, action='list_all'))
    except:
        pass

    return itemlist


def alpha_list(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)
    matches = soup.find("tbody")
    for elem in matches.find_all("tr"):
        info = elem.find("td", class_="MvTbTtl")
        thumb = elem.img["data-lazy-src"]
        url = info.a["href"]
        title = info.a.text.strip()
        try:
            year = elem.find("td", text=re.compile(r"\d{4}")).text
        except:
            year = '-'
        new_item = Item(channel=item.channel, title=title, url=url, thumbnail=thumb, infoLabels={"year": year})

        if elem.find("span", class_="TpTv BgA"):
            new_item.action = "seasons"
            new_item.contentSerieName = title
        else:
            new_item.action = "findvideos"
            new_item.contentTitle = title
        itemlist.append(new_item)

    tmdb.set_infoLabels_itemlist(itemlist, True)

    next_page = soup.find("a", class_="next page-numbers")["href"]

    itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=next_page, action='alpha_list'))

    return itemlist


def seasons(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url).find_all("div", class_="Wdgt AABox")

    infoLabels = item.infoLabels
    for elem in soup:
        season = elem.select('div[data-tab]')[0]["data-tab"]
        title = "Temporada %s" % season
        infoLabels["season"] = season
        itemlist.append(Item(channel=item.channel, title=title, url=item.url, action='episodesxseason',
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

    soup = create_soup(item.url).find_all("div", class_="Wdgt AABox")
    infoLabels = item.infoLabels
    season = infoLabels["season"]
    for elem in soup:
        if elem.select('div[data-tab]')[0]["data-tab"] == str(season):
            epi_list = elem.find_all("td", class_="MvTbTtl")
            for epi in epi_list:
                url = epi.a["href"]
                epi_num = scrapertools.find_single_match(url, "\d+x(\d+)")
                infoLabels["episode"] = epi_num
                title = "%sx%s - %s" % (season, epi_num, epi.a.text)

                itemlist.append(Item(channel=item.channel, title=title, url=url, action="findvideos",
                                     infoLabels=infoLabels))
            break
    tmdb.set_infoLabels_itemlist(itemlist, True)

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()
    soup = create_soup(item.url)

    infoLabels = item.infoLabels

    for btn in soup.find("ul", class_="TPlayerNv").find_all("li"):

        opt = btn["data-tplayernv"]
        lang, quality = btn.find_all("span")[-1].text.split(" - ")
        elem = soup.find("div", class_="TPlayerTb", id=opt)
        logger.debug(elem)
        if not elem.iframe:
            elem = BeautifulSoup(elem.text, "html5lib", from_encoding="utf-8")
            new_url = elem.iframe["src"]
        else:
            new_url = elem.iframe["data-lazy-src"]
        new_url = create_soup(new_url).find("div", class_="Video").iframe["src"]

        if "seriemega" in new_url:
            referer = new_url
            new_url = new_url.replace("/v/", "/api/source/")
            post = {"r": referer, "d": urlparse.urlparse(new_url)[1]}
            data = httptools.downloadpage(new_url, post=post).json
            url = data["data"][0]["file"]
        else:
            url = new_url

        itemlist.append(Item(channel=item.channel, title="%s [%s] [%s]", url=url, action='play',
                             language=IDIOMAS.get(lang, "VOSE"), quality=quality, infoLabels=infoLabels))

    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % (i.server, i.quality, i.language))
    # Requerido para FilterTools

    itemlist = filtertools.get_links(itemlist, item, list_language, list_quality)
    itemlist = sorted(itemlist, key=lambda i: i.server)
    # Requerido para AutoPlay

    autoplay.start(itemlist, item)
    if item.contentType != 'episode':
        if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos':
            itemlist.append(Item(channel=item.channel, title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
                                 url=item.url, action="add_pelicula_to_library", extra="findvideos",
                                 contentTitle=item.contentTitle))

    return itemlist


def section(item):
    logger.info()

    itemlist = list()

    if item.title == "Generos":
        soup = create_soup(host).find("ul", class_="sub-menu")
        action = "list_all"
    elif item.title == "Alfabetico":
        soup = create_soup(item.url).find("ul", class_="AZList")
        action = "alpha_list"

    for elem in soup.find_all("li"):
        url = elem.a["href"]
        title = elem.a.text
        itemlist.append(Item(channel=item.channel, title=title, action=action, url=url))

    return itemlist

def genres(item):
    logger.info()
    itemlist = list()

    soup = create_soup(host).find("ul", class_="sub-menu")
    matches = soup.find_all("a")
    for elem in matches:

        title = elem.text
        url = elem["href"]
        itemlist.append(Item(channel=item.channel, title=title, url=url, action="list_all"))

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

    item = Item()
    try:
        if categoria == 'peliculas':
            item.url = host + 'peliculas'
        itemlist = list_all(item)
        if itemlist[-1].title == 'Siguiente >>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist