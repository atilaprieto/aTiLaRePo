# -*- coding: utf-8 -*-
# -*- Channel PoseidonHD -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import re
from bs4 import BeautifulSoup

from core import tmdb
from core import httptools
from core.item import Item
from core import servertools
from core import scrapertools
from core import jsontools
from channelselector import get_thumb
from platformcode import config, logger
from channels import filtertools, autoplay

IDIOMAS = {'mx': 'Latino', 'dk': 'Latino', 'es': 'Castellano', 'en': 'VOSE', 'gb': 'VOSE', 'de': 'Alemán',
           "Latino": "Latino", "Español": "Castellano", "Subtitulado": "VOSE"}
list_language = list(IDIOMAS.values())

list_quality = []

list_servers = [
    'gvideo',
    'fembed'
    ]

host = 'https://tekilaz.org/'


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title='Peliculas', action='sub_menu',
                         thumbnail=get_thumb('movies', auto=True)))

    itemlist.append(Item(channel=item.channel, title='Series',  action='sub_menu',
                         thumbnail=get_thumb('tvshows', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url=host + '?s=',
                         thumbnail=get_thumb("search", auto=True),  extra='movie'))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def sub_menu(item):
    logger.info()

    itemlist = list()

    type = "movies" if item.title == "Peliculas" else item.title.lower()

    itemlist.append(Item(channel=item.channel, title='Destacadas', url='%scategory/destacadas/' % (host),
                         action='list_all', thumbnail=get_thumb('hot', auto=True), type=type))

    itemlist.append(Item(channel=item.channel, title='Todas', url=host + type, action='list_all',
                         thumbnail=get_thumb('all', auto=True), type=type))

    itemlist.append(
        Item(channel=item.channel, title='Generos', action='section', thumbnail=get_thumb('genres', auto=True),
             type=type))

    itemlist.append(Item(channel=item.channel, title='Por Año', action='section',
                         thumbnail=get_thumb('year', auto=True), type=type))

    return itemlist


def create_soup(url, post=None, unescape=False):
    logger.info()

    if post:
        data = httptools.downloadpage(url, post=post).data
    else:
        data = httptools.downloadpage(url).data

    if unescape:
        data = scrapertools.unescape(data)

    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")

    return soup


def get_language(lang_data):
    logger.info()

    language = list()

    lang_list = lang_data.find_all("span", class_="flag")
    for lang in lang_list:
        lang = scrapertools.find_single_match(lang["style"], '/flags/(.*?).png\)')
        if lang == 'en':
            lang = 'vose'
        if lang not in language:
            language.append(lang)
    return language


def section(item):
    logger.info()

    itemlist = list()

    soup = create_soup(host)

    if item.title == "Generos":
        matches = soup.find("li", id="menu-item-66646")
    else:
        matches = soup.find("section", id="torofilm_movies_annee-2")

    for elem in matches.find_all("li"):

        url = "%s/?type=%s" % (elem.a["href"], item.type)
        title = elem.a.text
        itemlist.append(Item(channel=item.channel, title=title, action="list_all", url=url, type=item.type))

    if item.title == "Generos":
        return itemlist

    return itemlist[::-1]


def list_all(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)
    matches = soup.find("section", class_="section movies")
    if not matches:
        matches = soup.find("div", id="aa-movies")
    for elem in matches.find_all("article", class_=re.compile(r"post (?:dfx|fcl|movies)")):

        type = item.type
        url = elem.a["href"]

        if item.type != "search" and (("/series/" in url and type != "series") or ("/movie" in url and type != "movies")):
            continue

        title = elem.h2.text
        thumb = elem.img["src"]

        year = "-"
        if not "series" in url:
            try:
                year = elem.find("span", class_="year").text
            except:
                pass

        new_item = Item(channel=item.channel, title=title, url=url, thumbnail=thumb, infoLabels={"year": year})

        if "series" in url:
            new_item.contentSerieName = title
            new_item.action = "seasons"
        else:
            new_item.contentTitle = title
            new_item.action = "findvideos"

        itemlist.append(new_item)

    tmdb.set_infoLabels_itemlist(itemlist, True)

    try:
        url_next_page = soup.find("a", text="PROXIMO")["href"]
    except:
        return itemlist

    itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=url_next_page, action='list_all', type=item.type))

    return itemlist


def seasons(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)

    matches = soup.find_all("li", class_="sel-temp")

    infoLabels = item.infoLabels

    for elem in matches:

        season = elem.a["data-season"]
        v_id = elem.a["data-post"]
        title = "Temporada %s" % season
        infoLabels["season"] = season

        itemlist.append(Item(channel=item.channel, title=title, action='episodesxseasons', v_id=v_id,
                             infoLabels=infoLabels))

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
    infoLabels = item.infoLabels
    season = infoLabels["season"]

    url = "%swp-admin/admin-ajax.php" % host
    post = {"action": "action_select_season", "season": season, "post": item.v_id}

    soup = create_soup(url, post, True)
    matches = soup.find_all("li")

    for elem in matches:
        url = elem.a["href"]
        title = elem.find("span", class_="num-epi").text
        epi_num = title.split("x")[1]
        infoLabels["episode"] = epi_num

        itemlist.append(Item(channel=item.channel, title=title, url=url, action='findvideos',
                             infoLabels=infoLabels))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()
    servers = {'drive': 'gvideo', 'fembed': 'fembed', "player": "oprem", "openplay": "oprem"}
    soup = create_soup(item.url)
    matches = soup.find("ul", class_="aa-tbs aa-tbs-video").find_all("li")

    for elem in matches:
        srv, lang = elem.find("span", class_="server").text.replace(" - ", "-").split("-")
        opt = elem.a["href"].replace("#","")
        try:
            url = soup.find("div", id="%s" % opt).find("iframe")["data-src"]
        except:
            continue
        if srv.lower() in ["waaw", "jetload"]:
           continue
        if srv.lower() in servers:
           srv = servers[srv.lower()]

        itemlist.append(Item(channel=item.channel, title=srv, url=url, action="play", infoLabels=item.infoLabels,
                             language=IDIOMAS.get(lang, lang), server=srv))

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
    try:
        data = create_soup(item.url).find("input")["value"]
        base_url = "%sr.php" % host
        post = {"data": data}
        url = httptools.downloadpage(base_url, post=post).url
        if "fs.poseidonhdd.com" in url:
            api_url = "%sr.php" % host.replace("https://", "https://fs.")
            v_id = scrapertools.find_single_match(url, r"\?h=([A-z0-9]+)")
            post = {"h": v_id}
            url = httptools.downloadpage(api_url, post=post).url
        itemlist.append(item.clone(url=url, server=""))
        itemlist = servertools.get_servers_itemlist(itemlist)
    except:
        pass

    return itemlist


def search(item, texto):
    logger.info()
    try:
        texto = texto.replace(" ", "+")
        item.url = item.url + texto
        item.type = "search"
        if texto != '':
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
        if categoria in ['peliculas']:
            item.url = host + 'movies'
        elif categoria == 'infantiles':
            item.url = host + 'category/animacion/'
        elif categoria == 'terror':
            item.url = host + 'category/terror/'
        item.type = "movies"
        itemlist = list_all(item)
        if itemlist[-1].title == 'Siguiente >>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist
