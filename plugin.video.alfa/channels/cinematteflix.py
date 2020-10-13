# -*- coding: utf-8 -*-
# -*- Channel CinematteFlix-*-
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


list_language = ["CAST", "VOSE"]

list_quality = []

list_servers = [
    'youtube',
    ]

host = 'https://www.cinematteflix.com/'


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title='Todas', url=host, action='list_all',
                         thumbnail=get_thumb('all', auto=True)))

    itemlist.append(Item(channel=item.channel, title='Destacadas',
                         url=host + "search/label/CINEMATTE%20FLIX%20DESTACADOS", action='list_all',
                         thumbnail=get_thumb('destacadas', auto=True)))

    itemlist.append(Item(channel=item.channel, title='Colecciones',
                         url=host + "search/label/CINEMATTE%20FLIX%20COLECCIONES", action='list_all',
                         thumbnail=get_thumb('colecciones', auto=True)))

    itemlist.append(Item(channel=item.channel, title='Generos', url=host, action='section',
                         thumbnail=get_thumb('all', auto=True)))

    # itemlist.append(
    #     item.clone(title="Buscar...", action="search", url=host + 'search?q=', thumbnail=get_thumb("search", auto=True),
    #                extra='movie'))

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

    soup = create_soup(item.url).find("div", id="PageList2")
    matches = soup.find_all("li")

    for elem in matches[1:]:
        title = elem.a.text.lower().replace("cine de ", "").capitalize()
        if "colecciones" in title:
            continue
        url = elem.a["href"]
        itemlist.append(Item(channel=item.channel, url=url, action="list_all", title=title))

    itemlist = sorted(itemlist, key=lambda i: i.title)

    return itemlist


def list_all(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)
    matches = soup.find_all("article", class_="post-outer-container")

    for elem in matches:
        try:
            url = elem.h3.a["href"].strip()
            info = elem.find("div", class_="r-snippetized").text.strip()

            if "serie" in info.lower() or "temporada" in info.lower():
                continue

            if "subt" in info.lower():
                lang = "VOSE"
            else:
                lang = "CAST"
            title = info.split("|")[0]
            title = re.sub(r" \(.*?\)", "", title)
            year = scrapertools.find_single_match(info, "\d{4}")

            new_item = Item(channel=item.channel, title=title.capitalize(), url=url, infoLabels={"year": year})

            if "/coleccion" in url:
                new_item.action = "list_collection"
            else:
                new_item.action = "findvideos"
                new_item.contentTitle = title
                new_item.language = lang

            itemlist.append(new_item)
        except:
            pass
    tmdb.set_infoLabels_itemlist(itemlist, True)

    try:
        url_next_page = soup.find("a", class_="blog-pager-older-link")["href"]
    except:
        return itemlist
    if len(itemlist) > 20:
        itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=url_next_page, action='list_all'))

    return itemlist


def list_collection(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)

    pag = soup.find("script", text=re.compile("var pagina"))
    if pag:
        url = scrapertools.find_single_match(pag.text, 'var pagina="([^"]+)"')
        return list_all(item.clone(url=url))

    matches = soup.find_all("iframe")
    cnt = 1
    for elem in matches:
        url = elem["src"]
        if "youtube" not in url:
            continue
        try:
            info_url = "https://www.youtube.com/oembed?url=%s&format=json" % url.replace("/embed/", "/watch?v=")
            info = httptools.downloadpage(info_url).json
            title = info["title"].replace(" HD", "")
            thumb = info["thumbnail_url"]
            ct = title
        except:
            ct = ""
            no_title = re.sub(r":|colecciÓn|'|\d+", "", item.title.lower()).strip()
            if cnt == 1:
                title = "%s" % (no_title)
            else:
                title = "%s %s" % (no_title, cnt)

            thumb = item.thumb
            cnt += 1

        itemlist.append(Item(channel=item.channel, title=title.capitalize(), contentTitle=ct, action="findvideos", url=url,
                             language=item.language, thumbnail=thumb, infoLabels={"year": "-"}))

    tmdb.set_infoLabels_itemlist(itemlist, True)


    return itemlist


def findvideos(item):
    logger.info()
    itemlist = list()

    if not "youtube" in item.url:
        soup = create_soup(item.url)
        url = soup.find("iframe")["src"]
    else:
        url = item.url

    itemlist.append(Item(channel=item.channel, title="%s", action="play", url=url,
                         language=item.language, infoLabels=item.infoLabels))

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

