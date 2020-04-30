# -*- coding: utf-8 -*-
# -*- Channel SeriesFlix -*-
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

host = 'https://seriesflix.co/'
IDIOMAS = {"Latino": "LAT"}
list_language = IDIOMAS.values()
list_servers = ['uqload', 'fembed', 'mixdrop', 'supervideo', 'mystream']
list_quality = []


def create_soup(url, post=None, headers=None):
    logger.info()

    data = httptools.downloadpage(url, post=post, headers=headers).data
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")

    return soup


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)
    itemlist = list()

    itemlist.append(Item(channel=item.channel, title="Ultimas", action="list_all",
                         url="%swp-admin/admin-ajax.php" % host, thumbnail=get_thumb("last", auto=True), first=0))

    itemlist.append(Item(channel=item.channel, title="Mas Vistas", action="list_all",
                         url="%swp-admin/admin-ajax.php" % host, thumbnail=get_thumb("more watched", auto=True), first=0))

    itemlist.append(Item(channel=item.channel, title="Todas", action="list_all", url=host + "ver-series-online",
                         thumbnail=get_thumb("all", auto=True), first=0))

    itemlist.append(Item(channel=item.channel, title="Productoras", action="sub_menu", url=host))

    itemlist.append(Item(channel=item.channel, title="Generos", action="section", url=host,
                         thumbnail=get_thumb("genres", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Alfabetico", action="section", url=host,
                         thumbnail=get_thumb("alphabet", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url=host + "?s=",
                         thumbnail=get_thumb("search", auto=True)))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def sub_menu(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url).find("li", id="menu-item-1888")

    matches = soup.find_all("li")

    for elem in matches:

        url = elem.a["href"]
        title = elem.a.text

        itemlist.append(Item(channel=item.channel, url=url, title=title, action="list_all", first=0))

    return itemlist


def list_all(item):
    logger.info()

    itemlist = list()
    next = False
    if item.title == "Mas Vistas":
        post = {"action": "action_changue_post_by", "type": "#Views", "posttype": "series"}
        matches = create_soup(item.url, post=post)
    elif item.title == "Ultimas":
        post = {"action": "action_changue_post_by", "type": "#Latest", "posttype": "series"}
        matches = create_soup(item.url, post=post)
    else:
        soup = create_soup(item.url)
        matches = soup.find("ul", class_=re.compile(r"MovieList Rows AX A04 B03 C20 D03 E20 Alt"))

    if not matches:
        return itemlist

    matches = matches.find_all("article")

    first = item.first
    last = first + 25
    if last >= len(matches):
        last = len(matches)
        next = True

    for elem in matches[first:last]:
        url = elem.a["href"]
        title = elem.find(["div", "ul"], class_="Title").text
        thumb = elem.img["data-src"]

        itemlist.append(Item(channel=item.channel, url=url, title=title, thumbnail=thumb, action="seasons",
                        contentSerieName=title))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    if not next:
        url_next_page = item.url
        first = last
    else:
        try:
            url_next_page = soup.find("div", class_="nav-links").find_all("a")[-1]
            if url_next_page.text:
                url_next_page = ''
            else:
                url_next_page = url_next_page["href"]
        except:
            return itemlist

        url_next_page = '%s' % url_next_page
        first = 0

    if url_next_page and len(matches) > 26:
        itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=url_next_page, action='list_all',
                             first=first))

    return itemlist


def section(item):
    logger.info()

    itemlist = list()

    if item.title == "Generos":
        soup = create_soup(host).find("div", id="toroflix_genres_widget-2")
        action = "list_all"
    elif item.title == "Alfabetico":
        soup = create_soup(item.url).find("ul", class_="AZList")
        action = "alpha_list"

    for elem in soup.find_all("li"):
        url = elem.a["href"]
        title = elem.a.text
        itemlist.append(Item(channel=item.channel, title=title, action=action, url=url, first=0))

    return itemlist


def alpha_list(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)
    matches = soup.find("tbody")
    if not matches:
        return itemlist
    for elem in matches.find_all("tr"):
        info = elem.find("td", class_="MvTbTtl")
        thumb = elem.img["data-src"]
        url = info.a["href"]
        title = info.a.text.strip()

        itemlist.append(Item(channel=item.channel, title=title, url=url, action="seasons", thumbnail=thumb,
                             contentSerieName=title))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    return itemlist


def seasons(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url).find_all("section", class_="SeasonBx AACrdn")

    infoLabels = item.infoLabels
    for elem in soup:
        season = elem.a.span.text
        url = elem.a["href"]
        title = "Temporada %s" % season
        infoLabels["season"] = season
        itemlist.append(Item(channel=item.channel, title=title, url=url, action='episodesxseason',
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
    matches = soup.find_all("tr", class_="Viewed")
    infoLabels = item.infoLabels
    season = infoLabels["season"]
    for elem in matches:
        url = elem.find("td", class_="MvTbTtl").a["href"]
        epi_num = elem.find("span", class_="Num").text
        epi_name = elem.find("td", class_="MvTbTtl").a.text
        infoLabels["episode"] = epi_num
        title = "%sx%s - %s" % (season, epi_num, epi_name)

        itemlist.append(Item(channel=item.channel, title=title, url=url, action="findvideos",
                             infoLabels=infoLabels))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()
    soup = create_soup(item.url)

    term_id = soup.find("div", class_="VideoPlayer")

    bloq = soup.find("ul", class_="ListOptions")
    for elem in bloq.find_all("li"):
        url = "https://seriesflix.co/?trembed=%s&trid=%s&trtype=2" % (elem["data-key"], elem["data-id"])
        server = elem.find("p", class_="AAIco-dns").text
        if server.lower() == "embed":
            server = "Mystream"
        lang = elem.find("p", class_="AAIco-language").text
        qlty = elem.find("p", class_="AAIco-equalizer").text
        title = "%s [%s]" % (server, lang)
        itemlist.append(Item(channel=item.channel, title=title, url=url, action='play',
                             language=IDIOMAS.get(lang, lang), infoLabels=item.infoLabels,
                             server=server))


    #Requerido para FilterTools

    itemlist = filtertools.get_links(itemlist, item, list_language)

    #Requerido para AutoPlay

    autoplay.start(itemlist, item)

    return itemlist


def play(item):
    logger.info()

    itemlist = list()

    url = create_soup(item.url).find("div", class_="Video").iframe["src"]

    itemlist.append(item.clone(url=url, server=""))
    itemlist = servertools.get_servers_itemlist(itemlist)
    return itemlist


def search(item, texto):
    logger.info()
    try:
        texto = texto.replace(" ", "+")
        if texto != '':
            item.url += texto
            item.first = 0
            return list_all(item)
        else:
            return []
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
