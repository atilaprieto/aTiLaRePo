# -*- coding: utf-8 -*-
# -*- Channel SeriesDanko -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-


import re
import urlparse
import string
from channels import filtertools
from bs4 import BeautifulSoup
from core import httptools
from core import scrapertools
from core import servertools
from core.item import Item
from core import tmdb
from channels import autoplay
from platformcode import config, logger

HOST = 'https://seriesdanko.net/'
IDIOMAS = {'es': 'Español', 'la': 'Latino', 'vos': 'VOS', 'vo': 'VO', 'sub': 'VOSE', 'en': 'VO'}
list_idiomas = IDIOMAS.values()
list_servers = ['powvideo', 'gamovideo', 'streamplay', 'flashx', 'nowvideo', 'thevideo']
list_quality = []


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

    autoplay.init(item.channel, list_servers, list_quality)
    itemlist = list()

    itemlist.append(Item(channel=item.channel, title="Novedades", action="novedades", url=HOST))
    itemlist.append(Item(channel=item.channel, title="Ultimas series", action="section", url=HOST))
    itemlist.append(Item(channel=item.channel, title="Más vistas", action="section", url=HOST))
    itemlist.append(Item(channel=item.channel, title="Listado Alfabético", action="alpha", url=HOST))
    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url=HOST + "/?s="))

    itemlist = filtertools.show_option(itemlist, item.channel, list_idiomas, list_quality)

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def novedades(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url).find("div", class_="main-post")

    for elem in soup.find_all("article"):
        url = elem.a["href"]
        thumb = elem.find("div", class_="text-center mt-10").img["src"]
        lang = scrapertools.find_single_match(elem.find("h3").img["src"], "/([^\.]+)\.png")
        info = elem.find("h3").find_all("span")
        title = "%s - %s" % (info[0].text, info[1].text)

        itemlist.append(Item(channel=item.channel, title=title, url=url, thumbnail=thumb, action="findvideos",
                             contentSerieName=info[0].text, language=lang))

    tmdb.set_infoLabels_itemlist(itemlist, True)
    return itemlist


def section(item):
    logger.info()

    itemlist = list()
    if "vistas" in item.title:
        value = "HTML3"
    else:
        value = "HTML2"
    soup = create_soup(item.url).find("div", id=value)

    for elem in soup.find_all("li"):
        url = elem.a["href"]
        title = elem.a.text

        itemlist.append(Item(channel=item.channel, url=url, title=title, contentSerieName=title, action="seasons",
                        context=filtertools.context(item, list_idiomas, list_quality)))
    tmdb.set_infoLabels_itemlist(itemlist, True)
    return itemlist


def alpha(item):
    logger.info()

    itemlist = list()

    for letra in string.ascii_uppercase:
        url = "%s/lista-de-series/%s" % (HOST, letra)
        itemlist.append(Item(channel=item.channel, action="generic_list", title=letra, url=url, mode='alpha'))

    return itemlist


def seasons(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url).find_all("h4", class_="panel-title")
    infoLabels = item.infoLabels
    for elem in soup:
        title = elem.a.text.strip()
        season = scrapertools.find_single_match(title, "Temporada (\d+)")
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
                             contentSerieName=item.contentSerieName,
                             ))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []
    templist = seasons(item)
    for tempitem in templist:
        itemlist += episodesxseason(tempitem)
    return itemlist


def episodesxseason(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url).find("table", class_="table table-hover")

    infoLabels = item.infoLabels

    for elem in soup.find_all("tr"):

        language = list()
        try:
            season_episode = scrapertools.find_single_match(elem.a.text, "(\d+x\d+)").split("x")
            title = "%sx%s - Episodio %s" % (season_episode[0], season_episode[1], season_episode[1])
            if int(season_episode[0]) != item.infoLabels["season"]:
                continue
            url = elem.a["href"]

            for lang in elem.find_all("img"):
                language.append(IDIOMAS[scrapertools.find_single_match(lang["data-lazy-src"], "language/([^\.]+)\.png")])

            infoLabels["episode"] = season_episode[1]

            itemlist.append(Item(channel=item.channel, title=title, url=url, action="findvideos",
                                 language=language, infoLabels=infoLabels))
        except:
            pass

    itemlist = filtertools.get_links(itemlist, item, list_idiomas, list_quality)
    tmdb.set_infoLabels_itemlist(itemlist, True)

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url).find("div", id="enlaces")

    for elem in soup.tbody.find_all("td", class_="linkComent text-center"):
        url = elem.a["data-enlace"]
        lang = elem.a["data-language"]
        itemlist.append(Item(channel=item.channel, url=url, title="%s", action="play", language=IDIOMAS[lang]))

    itemlist = servertools.get_servers_itemlist(itemlist, lambda x: x.title % x.server)

    # Requerido para FilterTools

    itemlist = filtertools.get_links(itemlist, item, list_idiomas, list_quality)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    return itemlist


def generic_list(item):
    logger.info()

    itemlist = list()
    if item.mode == "alpha":
        soup = create_soup(item.url).find("div", class_="main-post").find_all("article")
    else:
        soup = create_soup(item.url).find("div", class_="main-cont left").find_all("article")

    for elem in soup:
        url = elem.a["href"]
        title = elem.a.text.strip()
        thumb = elem.img["src"]

        itemlist.append(Item(channel=item.channel, title=title, thumbnail=thumb, url=url, action="seasons",
                             contentSerieName=title, context=filtertools.context(item, list_idiomas, list_quality)))

    tmdb.set_infoLabels_itemlist(itemlist, True)
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto
    item.mode = 'search'
    if texto != '':
        return generic_list(item)
    else:
        return []
