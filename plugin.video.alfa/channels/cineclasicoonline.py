# -*- coding: utf-8 -*-
# -*- Channel CineClasico Online -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

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

IDIOMAS = {'Spanish': 'CAST', 'VOSE': 'VOSE'}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['supervideo']

host = "https://cinemaclasic.atwebpages.com/"

def mainlist(item):
    logger.info()

    itemlist = list()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, title="Todas", url=host+'pelicula', action="list_all",
                         thumbnail=get_thumb('all', auto=True), first=0))

    itemlist.append(Item(channel=item.channel, title="Generos", action="genres",
                         thumbnail=get_thumb('genres', auto=True)))
    
    itemlist.append(Item(channel=item.channel, title="Directores", action="section",
                        thumbnail=get_thumb('colections', auto=True)))
    
    itemlist.append(Item(channel=item.channel, title="Actores", action="section",
                        thumbnail=get_thumb('actors', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Años", action="year",
                        thumbnail=get_thumb('year', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Buscar...",  url=host + '?s=',  action="search",
                         thumbnail=get_thumb('search', auto=True)))

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


def list_all(item):
    logger.info()

    itemlist = list()
    next = False

    soup = create_soup(item.url)
    matches = soup.find("div", class_="content").find_all("article", id=re.compile(r"^post-\d+"))

    first = item.first
    last = first + 25
    if last >= len(matches):
        last = len(matches)
        next = True

    for elem in matches[first:last]:

        info_1 = elem.find("div", class_="poster")
        info_2 = elem.find("div", class_="data")

        thumb = info_1.img["src"]
        title = info_1.img["alt"].split("-")[0].strip() if "-" in info_1.img["alt"] else info_1.img["alt"]
        title = re.sub("VOSE", "", title)
        url = info_1.a["href"]
        try:
            year = info_2.find("span", text=re.compile(r"\d{4}")).text.split(",")[-1].strip()
        except:
            year = "-"

        itemlist.append(Item(channel=item.channel, title=title, url=url, action='findvideos',
                             thumbnail=thumb, contentTitle=title, infoLabels={'year': year}))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    if not next:
        url_next_page = item.url
        first = last
    else:
        try:
            url_next_page = soup.find_all("a", class_="arrow_pag")[-1]["href"]
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

    soup = create_soup(host)

    if item.title == "Directores":
        matches = soup.find("aside", id="tag_cloud-6")

    elif item.title == "Actores":
        matches = soup.find("aside", id="tag_cloud-4")

    for elem in matches.find_all("a"):
        url = elem["href"]
        title = elem["aria-label"]
        itemlist.append(Item(channel=item.channel, title=title, action="list_all", url=url, first=0))

    return itemlist

def genres(item):
    logger.info()

    itemlist = list()

    soup = create_soup(host)

    matches = soup.find("ul", id="menu-generos")

    for elem in matches.find_all("li"):
        url = elem.a["href"]
        title = elem.a.text
        itemlist.append(Item(channel=item.channel, title=title, action="list_all", url=url, first=0))

    return itemlist

def year(item):
    logger.info()
    import datetime
    itemlist = list()

    now = datetime.datetime.now()
    c_year = now.year - 2
    l_year = 1950
    year_list = list(range(l_year, c_year))

    for year in year_list:
        year = str(year)
        url = '%s/ano/%s/' % (host, year)
        
        itemlist.append(Item(channel=item.channel, title=year, url=url, thumbnail=item.thumbnail,
                             action="list_all", type=item.type, first=0))
    itemlist.reverse()
    
    itemlist.append(Item(channel=item.channel, title='Introduzca otro año...', url='',
                                 action="year_cus", first=0, thumbnail=get_thumb("years.png")))

    return itemlist

def year_cus(item):
    from platformcode import platformtools
    heading = 'Introduzca Año (4 digitos)'
    year = platformtools.dialog_numeric(0, heading, default="")
    item.url = '%s/ano/%s/' % (host, year)
    item.action = "list_all"
    if year and len(year) == 4:
        return list_all(item)

def findvideos(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url).find("div", id="videos")
    matches = soup.find("div", class_="links_table")
    added = list()
    from channels.clubdecine import findvideos as fv
    for elem in matches.find_all("tr", id=re.compile(r"link-\d+")):
        links = elem.find_all("td")

        url = links[0].a["href"]
        lang = links[1].text
        server = scrapertools.find_single_match(links[0].img["src"], r"domain=([^\.]+)\.")
        if server == "my":
            server = "mailru"
        if server == "mycinedesiempre":
            redir = create_soup(url)
            url = redir.find("a", id="link")["href"]
            if re.sub(r"-\d+/", "/", url) not in added:
                itemlist.extend(fv(item.clone(url=url))[:-1])
                added.append(url)
        else:
            itemlist.append(Item(channel=item.channel, title='%s', action='play', url=url, server=server,
                                 language=IDIOMAS.get(lang, "VOSE"), infoLabels=item.infoLabels))

    itemlist = servertools.get_servers_itemlist(itemlist)

    # Requerido para FilterTools

    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos':
        itemlist.append(Item(channel=item.channel, title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
                             url=item.url, action="add_pelicula_to_library", extra="findvideos",
                             contentTitle=item.contentTitle))

    return itemlist


def play(item):
    logger.info()

    itemlist = list()

    item.server = ""
    if host in item.url:
        url = create_soup(item.url).find("a", id="link")["href"]
        itemlist.append(item.clone(url=url))
    else:
        itemlist.append(item)
    itemlist = servertools.get_servers_itemlist(itemlist)
    return itemlist


def search_results(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)

    for elem in soup.find_all("div", class_="result-item"):

        url = elem.a["href"]
        thumb = elem.img["src"]
        title = elem.img["alt"]
        title = elem.img["alt"].split("-")[0].strip() if "-" in elem.img["alt"] else elem.img["alt"]
        year = elem.find("span", class_="year").text

        itemlist.append(Item(channel=item.channel, title=title, contentTitle=title, url=url, thumbnail=thumb,
                             action='findvideos', infoLabels={'year': year}))

    tmdb.set_infoLabels_itemlist(itemlist, True)
    return itemlist


def search(item, texto):
    logger.info()
    try:
        texto = texto.replace(" ", "+")
        item.url = item.url + texto
        item.first = 0
        if texto != '':
            return search_results(item)
        else:
            return []
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []