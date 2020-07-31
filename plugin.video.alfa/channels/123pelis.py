# -*- coding: utf-8 -*-
# -*- Channel 123Pelis -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
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

PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

IDIOMAS = {"es": "CAST", "mx": "LAT", "en": "VOSE"}
list_language = IDIOMAS.values()
list_quality = []
list_servers = ["directo", "fembed", "mixdrop", "doodstream", "clipwatching", "cloudvideo"]

host = "https://123pelis.fun/"


def mainlist(item):
    logger.info()


    itemlist = list()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, title="Peliculas", action="sub_menu",
                         thumbnail=get_thumb("movies", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Series", action="sub_menu",
                         thumbnail=get_thumb("tvshows", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Castellano", url=host + "tag/castellano", action="list_all",
                         thumbnail=get_thumb("cast", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Latino", url=host + "tag/latino", action="list_all",
                         thumbnail=get_thumb("lat", auto=True)))

    itemlist.append(Item(channel=item.channel, title="VOSE", url=host + "tag/subtitulado", action="list_all",
                         thumbnail=get_thumb("vose", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Buscar...", url=host + "?s=", action="search",
                         thumbnail=get_thumb("search", auto=True)))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def sub_menu(item):
    logger.info()

    itemlist = list()
    if item.title == "Peliculas":
        get_type = "movie"
    else:
        get_type = "tv"

    itemlist.append(Item(channel=item.channel, title="Todas", url=host+item.title.lower()[:-1], action="list_all",
                         thumbnail=get_thumb("all", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Mas Vistas", url=host + "tendencias/?get=%s" % get_type,
                         action="list_all", thumbnail=get_thumb("more watched", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Netflix", url=host + "tag/%s-netflix" % item.title.lower()[:-1],
                         action="list_all", thumbnail=get_thumb("more watched", auto=True)))

    return itemlist


def create_soup(url, referer=None, unescape=False):
    logger.info()

    if referer:
        data = httptools.downloadpage(url, headers={"Referer": referer}).data
    else:
        data = httptools.downloadpage(url).data

    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")

    return soup


def list_all(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)
    matches = soup.find("div", class_="content")
    for elem in matches.find_all("article", id=re.compile(r"^post-\d+")):

        info_1 = elem.find("div", class_="poster")
        info_2 = elem.find("div", class_="data")

        thumb = info_1.img["src"]
        title = info_1.img["alt"]
        title = re.sub("VOSE", "", title)
        url = info_1.a["href"]
        try:
            year = info_2.find("span", text=re.compile(r"\d{4}")).text.split(",")[-1]
        except:
            pass
        new_item = Item(channel=item.channel, url=url, title=title, thumbnail=thumb, infoLabels={"year": year.strip()})

        if "serie" in url:
            new_item.action = "seasons"
            new_item.contentSerieName = title
        else:
            new_item.action = "findvideos"
            new_item.contentTitle = title

        itemlist.append(new_item)

    tmdb.set_infoLabels_itemlist(itemlist, True)
    try:
        next_page = soup.find_all("a", class_="arrow_pag")[-1]["href"]
        itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=next_page, action="list_all"))
    except:
        pass

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

        itemlist.append(Item(channel=item.channel, title=title, url=item.url, action="episodesxseasons",
                             infoLabels=infoLabels))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    if config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(
            Item(channel=item.channel, title="[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]", url=item.url,
                 action="add_serie_to_library", extra="episodios", contentSerieName=item.contentSerieName))

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

            itemlist.append(Item(channel=item.channel, title=title, url=url, action="findvideos",
                                 infoLabels=infoLabels))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []
    templist = seasons(item)
    for tempitem in templist:
        itemlist += episodesxseasons(tempitem)

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
        lang = elem.find("span", class_="flag").img["data-src"]
        lang = scrapertools.find_single_match(lang, r"flags/([^\.]+)\.png")
        data = httptools.downloadpage(doo_url, post=post, headers=headers).json
        if not data:
            continue
        url = data["embed_url"]
        if "hideload" in url:
            url = unhideload(url)
        if "pelis123" in url:
            itemlist.extend(get_premium(item, url, lang))
        elif not "onlystream" in url:
            itemlist.append(Item(channel=item.channel, title="%s", action="play", url=url,
                                 language=IDIOMAS.get(lang, "VOSE"), infoLabels=item.infoLabels))
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


def get_premium(item, url, lang):
    logger.info()

    itemlist = list()

    from lib.generictools import dejuice
    data = httptools.downloadpage(url).data
    dejuiced = dejuice(data)
    patron = r'"file":"([^"]+)","label":"(\d+P)"'
    matches = re.compile(patron, re.DOTALL).findall(dejuiced)
    for url, qlty in matches:
        itemlist.append(Item(channel=item.channel, title="%s", action="play", url=url,
                             language=IDIOMAS.get(lang, "VOSE"), quality=qlty, infoLabels=item.infoLabels))

    return itemlist


def unhideload(url):
    logger.info()
    server_dict = {"ad": "https://videobin.co/embed-",
                   "jd": "https://clipwatching.com/embed-",
                   "vd": "https://jetload.net/e/",
                   "ud": "https://dood.watch/e/",
                   "ld": "https://dood.watch/e/",
                   "gd": "https://mixdrop.co/e/",
                   "hd": "https://stream.kiwi/e/",
                   "kd": "https://play.pelis123.fun/e/",
                   "pd": "https://cloudvideo.tv/embed-",
                   "md": "https://feurl.com/v/",
                   "td": "https://videomega.co/e/"}

    server = scrapertools.find_single_match(url, r"(\wd)=")
    server = server_dict.get(server, server)
    hash_ = url.split("=")[1].split("&")[0]
    inv = hash_[::-1]
    result = inv.decode("hex")
    url = "%s%s" % (server, result)

    return url


def search_results(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)

    for elem in soup.find_all("div", class_="result-item"):

        url = elem.a["href"]
        thumb = elem.img["src"]
        title = elem.img["alt"]
        year = elem.find("span", class_="year").text

        itemlist.append(Item(channel=item.channel, title=title, contentTitle=title, url=url, thumbnail=thumb,
                             action="findvideos", infoLabels={"year": year}))

    tmdb.set_infoLabels_itemlist(itemlist, True)
    return itemlist


def search(item, texto):
    logger.info()
    try:
        texto = texto.replace(" ", "+")
        item.url = item.url + texto
        item.first = 0
        if texto != "":
            return search_results(item)
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
        if categoria in ["peliculas"]:
            item.url = host + "pelicula"
        elif categoria == "castellano":
            item.url = host + "tag/castellano"
        elif categoria == "latino":
            item.url = host + "tag/latino"
        itemlist = list_all(item)
        if itemlist[-1].title == "Siguiente >>":
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist