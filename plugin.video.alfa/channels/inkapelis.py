# -*- coding: utf-8 -*-
# -*- Channel InkaPelis -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import re
from core import tmdb
from core import httptools
from core.item import Item
from core import scrapertools
from bs4 import BeautifulSoup
from channelselector import get_thumb
from platformcode import config, logger
from channels import filtertools, autoplay
import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int


IDIOMAS = {'latino': 'LAT', 'castellano': 'CAST', 'subtitulado': 'VOSE'}
list_language = list(IDIOMAS.values())

list_quality = []

list_servers = [
    'fembed',
    'streampe',
    'gounlimited',
    'mystream',
    'gvideo'
    ]

host = 'https://inkapelis.me/'


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title='Peliculas', action='menu_movies',
                         thumbnail=get_thumb('movies', auto=True)))

    itemlist.append(Item(channel=item.channel, title='Series', url=host + 'serie', action='list_all',
                         thumbnail=get_thumb('tvshows', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url=host + '?s=',
                         thumbnail=get_thumb("search", auto=True)))


    autoplay.show_option(item.channel, itemlist)

    return itemlist


def menu_movies(item):
    logger.info()

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title='Ultimas', url=host + 'genero/estrenos-hd', action='list_all',
                         thumbnail=get_thumb('all', auto=True)))

    itemlist.append(Item(channel=item.channel, title='Todas', url=host + 'pelicula', action='list_all',
                         thumbnail=get_thumb('all', auto=True)))

    itemlist.append(Item(channel=item.channel, title='Castellano', url=host + 'idioma/castellano', action='list_all',
                         thumbnail=get_thumb('cast', auto=True)))

    itemlist.append(Item(channel=item.channel, title='Latino', url=host + 'idioma/latino', action='list_all',
                         thumbnail=get_thumb('lat', auto=True)))

    itemlist.append(Item(channel=item.channel, title='VOSE', url=host + 'idioma/subtituladas', action='list_all',
                         thumbnail=get_thumb('vose', auto=True)))



    itemlist.append(Item(channel=item.channel, title='Generos', action='section',
                         thumbnail=get_thumb('genres', auto=True)))

    itemlist.append(Item(channel=item.channel, title='Por Año', action='section',
                         thumbnail=get_thumb('year', auto=True)))

    return itemlist


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
    base_url = "%s%s" % (host, "pelicula")
    soup = create_soup(base_url)

    is_genre = False
    if item.title == "Generos":
        matches = soup.find("ul", class_="genres scrolling")
        is_genre = True
    else:
        matches = soup.find("ul", class_="releases scrolling")

    for elem in matches.find_all("li"):
        url = elem.a["href"]
        title = elem.a.text
        if is_genre:
            title = re.sub(elem.a.i.text, "", elem.a.text)

        itemlist.append(Item(channel=item.channel, title=title, action="list_all", url=url, first=0))

    return itemlist


def list_all(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)
    matches = soup.find("div", class_="content").find_all("article", id=re.compile(r"^post-\d+"))

    for elem in matches:
        langs = list()
        info_1 = elem.find("div", class_="poster")
        info_2 = elem.find("div", class_="data")

        thumb = info_1.img["src"]
        title = re.sub(r" \(.*?\)", "", info_1.img["alt"])
        url = info_1.a["href"]
        try:
            lang_list = elem.find("div", class_="audio").find_all("div")
            for lang in lang_list:
                langs.append(lang["class"][0])
        except:
            langs = ""
        try:
            year = info_2.find("span", text=re.compile(r"\d{4}")).text.split(",")[-1].strip()
        except:
            year = "-"

        new_item = Item(channel=item.channel, title=title, url=url, thumbnail=thumb, language=langs,
                        infoLabels={"year": year})

        if "serie/" in url:
            new_item.contentSerieName = title
            new_item.action = "seasons"
        else:
            new_item.contentTitle = title
            new_item.action = "findvideos"

        itemlist.append(new_item)

    tmdb.set_infoLabels_itemlist(itemlist, True)

    try:
        url_next_page = soup.find("div", class_="pagination").find("span", class_="current").next_sibling["href"]
    except:
        return itemlist

    if url_next_page and len(matches) > 16:
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
    srv_list = {"fembed": "fembed", "playstp": "streamtape", "stream": "mystream", "goplay": "gounlimited",
                "drive": "gvideo", "meplay": "netutv"}

    soup = create_soup(item.url)
    matches = soup.find("div", id="playeroptions")
    if not matches:
        return itemlist
    for elem in matches.find_all("li"):
        post = {"action": "doo_player_ajax", "post": elem["data-post"], "nume": elem["data-nume"],
                "type": elem["data-type"]}
        headers = {"Referer": item.url}
        doo_url = "%swp-admin/admin-ajax.php" % host
        try:
            lang = elem.find("img", class_="lazyload")["data-src"]
            lang = scrapertools.find_single_match(lang, r"flags/([^\.]+)\.svg")
        except:
            lang = ""
        data = httptools.downloadpage(doo_url, post=post, headers=headers).data
        new_url = scrapertools.find_single_match(data, "src='([^']+)'")
        new_soup = create_soup(new_url, referer=item.url).find_all("a", class_="button-xlarge btn bt")
        for srv in new_soup[:-1]:
            url = srv["data-embed"]
            server = srv_list.get(srv.find("span", class_="serverx").text.lower(), "directo")
            itemlist.append(Item(channel=item.channel, title='%s', action='play', url=url, server=server,
                                 language=IDIOMAS.get(lang, "VOSE"), infoLabels=item.infoLabels))

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

    player = host.replace("https://", "https://players.")

    url = "%sedge-data" % player
    post = {"streaming": item.url}
    url = httptools.downloadpage(url, post=post).data

    if "/pembed" in url:
        v_id = scrapertools.find_single_match(url, "=CXx8MB([^$]+)")
        url = "https://feurl.com/v/%s" % v_id
    elif "/direct" in url:
        url = httptools.downloadpage("%s%s" % (player, url), add_referer=True).url

    item = item.clone(url=url)
    return [item]


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

    for elem in soup.find_all("article", class_="item movies"):
        url = elem.a["href"]
        thumb = elem.img["src"]
        title = elem.img["alt"]
        try:
            year = elem.find("span", class_="year").text
        except:
            year = '-'

        language = get_language(elem)

        new_item = Item(channel=item.channel, title=title, url=url, thumbnail=thumb,
                        language=language, infoLabels={'year': year})

        if "/serie" in url:
            new_item.action = "seasons"
            new_item.contentSerieName = new_item.title
            new_item.context = filtertools.context(item, list_language, list_quality)
        else:
            new_item.action = "findvideos"
            new_item.contentTitle = new_item.title


        itemlist.append(new_item)

    tmdb.set_infoLabels_itemlist(itemlist, True)

    try:
        url_next_page = soup.find_all("a", class_="arrow_pag")[-1]["href"]
    except:
        return itemlist

    itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=url_next_page, action='search_results'))

    return itemlist


def newest(categoria):
    logger.info()

    item = Item()
    try:
        if categoria in ['peliculas']:
            item.url = host + 'pelicula'
        elif categoria == 'latino':
            item.url = host + 'idioma/latino'
        elif categoria == 'castellano':
            item.url = host + 'idioma/castellano'
        elif categoria == 'infantiles':
            item.url = host + 'genero/animacion/'
        elif categoria == 'terror':
            item.url = host + 'genero/terror/'
        itemlist = list_all(item)
        if itemlist[-1].title == 'Siguiente >>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist
