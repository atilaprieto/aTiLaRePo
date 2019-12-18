# -*- coding: utf-8 -*-
# -*- Channel Destotal -*-
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

IDIOMAS = {'espanol': 'CAST', 'castellano': 'CAST', 'latino': 'LAT', 'sub': 'VOSE'}
list_language = IDIOMAS.values()
list_quality = []
list_servers = ['openload',  'streamango', 'videoob', 'rapidvideo', 'okru']

host = "https://www.destotal.com/"

def mainlist(item):
    logger.info()

    itemlist = list()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel,
                         title="Todas",
                         url=host+'peliculas',
                         action="list_all",
                         thumbnail=get_thumb('all', auto=True),
                         first=0
                         ))

    itemlist.append(Item(channel=item.channel,
                    title="Audio",
                    action="sub_menu",
                    thumbnail=get_thumb('audio', auto=True),
                    first=0
                         ))

    itemlist.append(Item(channel=item.channel,
                         title="Buscar",
                         url=host + '?s=',
                         action="search",
                         thumbnail=get_thumb('search', auto=True)
                         ))

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


def sub_menu(item):
    logger.info()

    itemlist = list()

    itemlist.append(
        Item(channel=item.channel,
             title="Castellano HD",
             action="list_all",
             url="%s%s" % (host, "?calidad=hd&audio=castellano"),
             thumbnail=get_thumb('cast', auto=True),
             first=0))

    itemlist.append(
        Item(channel=item.channel,
             title="Castellano SD",
             action="list_all",
             url="%s%s" % (host, "?calidad=sd&audio=castellano"),
             thumbnail=get_thumb('cast', auto=True),
             first=0))

    itemlist.append(
        Item(channel=item.channel,
             title="Latino HD",
             action="list_all",
             url="%s%s" % (host, "?calidad=hd&audio=latino"),
             thumbnail=get_thumb('lat', auto=True),
             first=0))

    itemlist.append(
        Item(channel=item.channel,
             title="Latino SD",
             action="list_all",
             url="%s%s" % (host, "?calidad=sd&audio=latino"),
             thumbnail=get_thumb('lat', auto=True),
             first=0))

    itemlist.append(
        Item(channel=item.channel,
             title="VOSE HD",
             action="list_all",
             url="%s%s" % (host, "?calidad=hd&audio=vose"),
             thumbnail=get_thumb('vose', auto=True),
             first=0))

    itemlist.append(
        Item(channel=item.channel,
             title="VOSE SD",
             action="list_all",
             url="%s%s" % (host, "?calidad=sd&audio=vose"),
             thumbnail=get_thumb('vose', auto=True),
             first=0))

    return itemlist


def list_all(item):
    logger.info()

    itemlist = list()
    next = False

    soup = create_soup(item.url).find("div", class_="content")

    matches = soup.find_all("article", id=re.compile(r"^post-\d+"))

    first = item.first
    last = first + 25
    if last >= len(matches):
        last = len(matches)
        next = True

    for elem in matches[first:last]:

        info_1 = elem.find("div", class_="poster")
        info_2 = elem.find("div", class_="data")

        thumb = info_1.img["src"]
        title = info_1.img["alt"]
        url = info_1.a["href"]
        year = info_2.find("span", text=re.compile(r"\d{4}")).text.strip()
        lang = languages_from_flags(info_1.find("div", class_="bandera"), "png")

        itemlist.append(Item(channel=item.channel, title=title, url=url, action='findvideos',
                             thumbnail=thumb, contentTitle=title, language=lang, infoLabels={'year': year}))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    if not next:
        url_next_page = item.url
        first = last
    else:
        try:
            url_next_page = soup.find("a", class_="arrow_pag")["href"]
        except:
            return itemlist

        url_next_page = '%s' % url_next_page
        first = 0

    if url_next_page and len(matches) > 26:
        itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=url_next_page, action='list_all',
                             first=first))

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url, unescape=True)

    sources = soup.find("div", class_="playex")
    langs = soup.find("ul", class_="idTabs sourceslist")

    for elem in sources.find_all("div", class_="play-box-iframe"):

        opt = elem["id"]
        url = elem.iframe["src"]
        if "hideload" in url:
            url = unhideload(url)

        lang_data = langs.find("a", href=re.compile(r"^#%s" % opt))
        lang = languages_from_flags(lang_data.span, "png")

        itemlist.append(Item(channel=item.channel, title='%s', action='play', url=url,
                             language=lang, infoLabels=item.infoLabels))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda x: x.title % x.server.capitalize())

    # Requerido para FilterTools

    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos':
        itemlist.append(Item(channel=item.channel, title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
                             url=item.url, action="add_pelicula_to_library", extra="findvideos",
                             contentTitle=item.contentTitle))

    return itemlist


def languages_from_flags(lang_data, ext):
    logger.info()
    language = []

    lang_list = lang_data.find_all("img")

    for lang in lang_list:
        lang = scrapertools.find_single_match(lang["src"], "(\w+).%s" % ext)

        language.append(IDIOMAS.get(lang, "VOSE"))
    return language


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
                             action='findvideos', infoLabels={'year': year}))

    tmdb.set_infoLabels_itemlist(itemlist, True)
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto
    item.first = 0
    if texto != '':
        return search_results(item)
    else:
        return []


def unhideload(url):
    logger.info()
    server_dict = {"od": "http://ok.ru/videoembed/",
                   "ed": "http://streamango.com/embed/",
                   "id": "https://oload.tv/embed/"}

    server = server_dict[scrapertools.find_single_match(url, "(\wd)=")]
    hash_ = url.split("=")[1].split("&")[0]
    inv = hash_[::-1]
    result = inv.decode('hex')
    url = "%s%s" % (server, result)
    return url