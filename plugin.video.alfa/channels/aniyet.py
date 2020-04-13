# -*- coding: utf-8 -*-
# -*- Channel AniYet -*-
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


host = 'https://aniyet.com/'

list_idiomas = ['LAT']
list_servers = ['directo', 'sendvid', 'uqload', 'yourupload', 'mp4upload', 'gounlimited', 'fembed']
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

    itemlist.append(Item(channel=item.channel, title="Novedades", action="list_all", url=host,
                         thumbnail=get_thumb("newest", auto=True)))

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
    soup = create_soup(item.url).find("ul", class_="MovieList NoLmtxt Rows AX A06 B04 C03 E20")
    if not soup:
        return itemlist

    for elem in soup.find_all("article"):

        url = elem.a["href"]
        title = elem.a.h3.text
        thumb = elem.find("img")["src"]

        itemlist.append(Item(channel=item.channel, url=url, title=title, contentSerieName=title, action="seasons",
                        thumbnail=thumb))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    return itemlist


def section(item):
    logger.info()

    itemlist = list()

    if item.title == "Generos":
        soup = create_soup(item.url).find("div", id="categories-2")
        action = "list_all"
    elif item.title == "Alfabetico":
        soup = create_soup(item.url).find("ul", class_="AZList")
        action = "alpha_list"

    for elem in soup.find_all("li"):
        url = elem.a["href"]
        title = elem.a.text
        itemlist.append(Item(channel=item.channel, title=title, action=action, url=url))

    return itemlist


def alpha_list(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url).find("tbody")
    if not soup:
        return itemlist
    for elem in soup.find_all("tr"):
        info = elem.find("td", class_="MvTbTtl")
        thumb = elem.find("td", class_="MvTbImg").a.img["src"]
        url = info.a["href"]
        title = info.a.text.strip()
        itemlist.append(Item(channel=item.channel, title=title, url=url, action='seasons', thumbnail=thumb,
                             contentSerieName=title))

    tmdb.set_infoLabels_itemlist(itemlist, True)

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
                epi_num = scrapertools.find_single_match(url, "episodio-(\d+)")
                infoLabels["episode"] = epi_num
                title = "%sx%s - %s" % (season, epi_num, epi.a.text)

                itemlist.append(Item(channel=item.channel, title=title, url=url, action="findvideos",
                                     infoLabels=infoLabels))
            break
    tmdb.set_infoLabels_itemlist(itemlist, True)

    return itemlist


def findvideos(item):
    logger.info()
    srv_list = {'Zeta-SV': 'sendvid', 'Zeta-CU': 'directo', 'Zeta-GD': 'uqload', 'Zeta-MP4': 'mp4upload',
                'StreamOnly': 'uqload', 'CloudVid': 'gounlimited',
                'EmbedFe': 'fembed', 'Upload': 'yourupload', 'LoadJet': 'jetload', 'Load': 'openload',
                'Mango': 'streamango', 'StreamVery': 'verystream', 'StreamNormal': 'netutv', }
    itemlist = list()
    soup = create_soup(item.url).find("ul", class_="TPlayerNv").find_all("li")
    infoLabels = item.infoLabels
    for btn in soup:
        opt = btn["data-tplayernv"]
        srv = srv_list.get(btn.text, 'directo')
        itemlist.append(Item(channel=item.channel, url=item.url, action='play', server=srv, opt=opt, language='LAT',
                        infoLabels=infoLabels))

    # Requerido para FilterTools

    itemlist = filtertools.get_links(itemlist, item, list_idiomas, list_quality)
    itemlist = sorted(itemlist, key=lambda i: i.server)
    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    return itemlist


def play(item):
    logger.info()
    itemlist = list()

    soup = create_soup(item.url).find("div", class_="TPlayerTb", id=item.opt)
    url = scrapertools.find_single_match(str(soup), 'src="([^"]+)"')
    url = scrapertools.decodeHtmlentities(url).replace("&#038;", "&")
    data = httptools.downloadpage(url, headers={"referer": item.url}, follow_redirects=False).data
    id = scrapertools.find_single_match(data, '<iframe.*?tid=([^&]+)&')
    hide = "https://aniyet.com/?trhide=1&trhex=%s" % id[::-1]
    referer = "https://aniyet.com/?trhide=1&tid=%s" % id
    data = httptools.downloadpage(hide, headers={"referer": referer}, follow_redirects=False)
    url = data.headers.get('location', '')
    if 'danimados' in url:
        data = httptools.downloadpage('https:'+url).data

        if item.server in ['sendvid']:
            url = scrapertools.find_single_match(data, '<iframe src="([^"]+)"')
        else:
            url = scrapertools.find_single_match(data, 'sources: \[{file: "([^"]+)"')

    srv = servertools.get_server_from_url(url)
    itemlist.append(item.clone(url=url, server=srv))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        texto = texto.replace(" ", "+")
        if texto != '':
            item.url += texto
            return list_all(item)
            return []
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

