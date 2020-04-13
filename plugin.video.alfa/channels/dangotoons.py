# -*- coding: utf-8 -*-

import re

from channels import renumbertools
from bs4 import BeautifulSoup
from channelselector import get_thumb
from core import httptools
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item
from platformcode import config, logger
from channels import autoplay

IDIOMAS = {'latino': 'Latino'}
list_language = IDIOMAS.values()
list_servers = [
                'okru',
                'rapidvideo'
                ]
list_quality = ['default']

host = "https://dangotoons.com"

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

def create_mainlist_item(data):
    
    category = data["category_dict"]
    data = data["data"]
    
    new_item = Item(channel=category["channel"], action="list_all", first=0,
        category= category["category"], thumbnail= category["thumbnail"])
    
    for key in data:
        new_item.__setattr__(key, data[key])
    
    return new_item

def mainlist(item):
    logger.info()
    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()
    
    category_all = {"thumbnail": get_thumb("all", auto=True), "category": "series",
        "channel": item.channel}
    category_series = category_all
    category_series["thumbnail"] = get_thumb("tvshows", auto=True)
    category_movies = {"thumbnail": get_thumb("movies", auto=True), "category": "peliculas",
        "channel": item.channel}
    categories = [
        {"data" :{"title": "Todos", "url": host+"/catalogo.php"}, "category_dict":category_all},
        {"data" :{"title": "Anime", "url": host+"/catalogo.php?t=anime&g=&o=0"}, "category_dict":category_series},
        {"data" :{"title": "Series Animadas", "url": host+"/catalogo.php?t=series-animadas&g=&o=0"}, 
            "category_dict":category_series},
        {"data" :{"title": "Series Animadas Adolescentes", "url": host+"/catalogo.php?t=series-animadas-r&g=&o=0"}, 
            "category_dict":category_series},
        {"data" :{"title": "Series Live Action", "url": host+"/catalogo.php?t=series-actores&g=&o=0"}, 
            "category_dict":category_series},
        {"data" :{"title": "Peliculas", "url": host+"/catalogo.php?t=peliculas&g=&o=0"}, "category_dict":category_movies},
        {"data" :{"title": "Especiales", "url": host+"/catalogo.php?t=especiales&g=&o=0"}, "category_dict":category_movies}
    ]

    for category in categories:
        itemlist.append(create_mainlist_item(category))
    
    itemlist.append(Item(channel=item.channel, action="search", title="Buscar",
        thumbnail=get_thumb("search", auto=True), first=0))

    itemlist = renumbertools.show_option(item.channel, itemlist)
    autoplay.show_option(item.channel, itemlist)
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = host +"/php/buscar.php"
    item.texto = texto
    if texto != '':
        return sub_search(item)
    else:
        return []


def sub_search(item):
    logger.info()
    itemlist = []
    post = "b=" + item.texto
    headers = {"X-Requested-With":"XMLHttpRequest"}
    data = httptools.downloadpage(item.url, post=post, headers=headers).data
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    for match in soup.find_all("a"):
        itemlist.append(Item(channel= item.channel, action= "seasons", title= match.text, 
            url = match["href"], category = "series", first=0, contentSerieName = match.text))
    tmdb.set_infoLabels(itemlist, seekTmdb=True)

    return itemlist

def list_all(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    match = soup.find("div", class_="listados")
    context = renumbertools.context(item)
    context2 = autoplay.context
    context.extend(context2)
    first = item.first
    last = first + 25
    matches = match.find_all("div", class_="serie")
    if last >= len(matches):
        last = len(matches)
    for elem in matches[first:last]:
        scrapedurl = elem.a["href"]
        scrapedthumbnail = elem.img["data-src"]
        scrapedtitle = elem.a.p.text
        scrapedplot = elem.find("span", class_="mini").text
        if item.category == "series":
            action = "seasons"
        else:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, title=scrapedtitle, contentSerieName=scrapedtitle,
            url=host + scrapedurl, plot=scrapedplot, thumbnail=scrapedthumbnail,
            action=action, context=context, category = item.category))

    tmdb.set_infoLabels(itemlist, seekTmdb=True)

    url_next_page = item.url
    first = last

    if url_next_page and len(matches) > 26:
        itemlist.append(Item(channel=item.channel, title="[COLOR cyan]Página Siguiente >>[/COLOR]", url=url_next_page, action='list_all',
            first=first))
    return itemlist

def seasons(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    soup = BeautifulSoup(data, "html5lib")
    match = soup.find("div", class_="listado")
    matches = match.find_all("div", class_="cajaTemporada")
    infoLabels = item.infoLabels
    if len(matches) == 0:
        title = "Temporada 1"
        infoLabels['season'] = 1
        itemlist.append(Item(channel=item.channel, title=title, contentSerieName=item.tile,
            url=item.url, plot=item.plot, thumbnail=item.thumbnail,
            action="episodesxseason", context=item.context, infoLabels=infoLabels))
    else:
        for elem in matches:
            title = elem.find("div", class_="titulo").text
            infoLabels['season'] = title.split(" ")[1]
            itemlist.append(Item(channel=item.channel, title=title, contentSerieName=item.tile,
                url=item.url, plot=item.plot, thumbnail=item.thumbnail,
                action="episodesxseason", context=item.context, infoLabels=infoLabels))
    if config.get_videolibrary_support() and len(itemlist) > 0 and not item.extra:
        itemlist.append(Item(channel=item.channel, url=item.url, action="add_serie_to_library",
                        extra="episodios", contentSerieName=item.contentSerieName,
                        title='[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]'))
    return itemlist

def episodesxseason(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    soup = BeautifulSoup(data, "html5lib")
    match = soup.find("div", class_="listado")
    matches = match.find_all("div", class_="cajaTemporada")
    if len(matches) == 0:
        episodes = match.find("div", class_="cajaCapitulos")
    else:
        for elem in matches:
            if elem.find("div", class_="titulo").text != item.title:
                continue
            episodes = elem.find("div", class_="cajaCapitulos")
    infoLabels = item.infoLabels
    for episode in episodes.find_all("li"):
        scrapedurl = "/"+episode.a["href"]
        scrapedtitle = episode.a.text
        infoLabels['episode'] = scrapedtitle.split(" - ")[0].split(": ")[1]
        title = "{}x{:02d} - {}".format(infoLabels['season'],infoLabels['episode'],scrapedtitle.split(" - ")[1])
        itemlist.append(Item(channel=item.channel, title=title, contentSerieName=item.tile,
            url=host + scrapedurl, plot=item.plot, thumbnail=item.thumbnail,
            action="findvideos", context=item.context, infoLabels=infoLabels))
    tmdb.set_infoLabels_itemlist(itemlist, True)
    return itemlist

def episodios(item):
    logger.info()
    itemlist = list()
    templist = seasons(item)
    for tempitem in templist:
        itemlist += episodesxseason(tempitem)

    return itemlist

def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    url_videos = scrapertools.find_single_match(data, 'var q = \[ \[(.+?)\] \]')
    matches = scrapertools.find_multiple_matches(url_videos, '"(.+?)"')
    for url in matches:
        url=url.replace('\/', '/')
        itemlist.append(item.clone(url=url, action="play", title= "%s"))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    
    autoplay.start(itemlist, item)

    if item.category=="peliculas" and config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(Item(channel=item.channel, url=item.url, contentSerieName=item.contentSerieName,
            title="[COLOR yellow]Añadir esta película a la videoteca[/COLOR]",
            action="add_pelicula_to_library"))

    return itemlist