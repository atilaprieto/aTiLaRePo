# -*- coding: utf-8 -*-
# -*- Channel BlogHorror -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import os
import re
from bs4 import BeautifulSoup
from core import httptools
from core import scrapertools
from core import tmdb
from core.item import Item
from platformcode import config, logger, subtitletools
from channelselector import get_thumb

host = 'http://bloghorror.com/'
fanart = 'http://bloghorror.com/wp-content/uploads/2015/04/bloghorror-2017-x.jpg'


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

    itemlist = list()

    itemlist.append(Item(channel=item.channel, fanart=fanart, title="Todas", action="list_all",
                         url=host+'/category/terror', thumbnail=get_thumb('all', auto=True)))

    itemlist.append(Item(channel=item.channel, fanart=fanart, title="Asiaticas", action="list_all",
                         url=host+'/category/asiatico', thumbnail=get_thumb('asiaticas', auto=True)))

    itemlist.append(Item(channel=item.channel, fanart=fanart, title = 'Buscar', action="search", url=host + '?s=', pages=3,
                         thumbnail=get_thumb('search', auto=True)))

    return itemlist


def list_all(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)

    matches = soup.find(id="primary").find_all("article")

    for elem in matches:

        title_data = elem.find("h3", class_="article-title").text.strip()
        title = title_data.replace(")", "").split(" (")
        url = elem.find("h3", class_="article-title").a["href"]
        thumb = elem.find("div", class_="data-bg-hover")["data-background"]
        try:
            year = title[1]
        except:
            year = "-"

        if "serie" in url:
            continue

        itemlist.append(Item(channel=item.channel, title=title[0], url=url, contentTitle=title[0], thumbnail=thumb,
                             action="findvideos", infoLabels={"year": year}))

    tmdb.set_infoLabels_itemlist(itemlist, True)


    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

    # Paginacion

    if itemlist:

        try:
            next_page = soup.find("div", class_="navigation").find("a", class_="next")["href"]

            if next_page != '':
                itemlist.append(Item(channel=item.channel, fanart=fanart, action="list_all", title='Siguiente >>>',
                                     url=next_page))
        except:
            pass

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()
    urls_list = list()
    sub_url = ''

    soup = create_soup(item.url).find("div", class_="entry-content").find("div")
    quality = scrapertools.find_single_match(soup.text, r"Calidad: ([^\n]+)\n")
    video_data = soup.find_all("a")

    for link in video_data:

        if link["data-wpel-link"] == "external":
            sub_url = link["href"]
        else:
            urls_list.append(link["href"])

    for url in urls_list:

        if not sub_url:
            sub = ''
            lang = 'VO'
        else:
            try:
                sub = subtitletools.get_from_subdivx(sub_url)
            except:
                sub = ''
            lang = 'VOSE'

        itemlist.append(Item(channel=item.channel, title="%s", url=url, action="play", quality=quality,
                             language=lang, subtitle=sub, server="torrent", infoLabels=item.infoLabels))

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos':
        itemlist.append(Item(channel=item.channel,
                             title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
                             url=item.url,
                             action="add_pelicula_to_library",
                             extra="findvideos",
                             contentTitle=item.contentTitle
                             ))

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
        if categoria in ['peliculas', 'terror', 'torrent']:
            item.url = host
        itemlist = list_all(item)
        if itemlist[-1].title == 'Siguiente >>>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist
