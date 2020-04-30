# -*- coding: utf-8 -*-

import re
import string

from channels import renumbertools
from bs4 import BeautifulSoup
from channelselector import get_thumb
from core import httptools
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item
from platformcode import config, logger
from channels import filtertools
from channels import autoplay
from lib import gktools

IDIOMAS = {'latino': 'Latino'}
list_language = IDIOMAS.values()
list_servers = []
list_quality = ['default']


host = "https://peliculasdisneylatino.blogspot.com"

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
    thumb_movies = get_thumb("movies", auto=True)
    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    url = host+"/search/label/"

    itemlist.append(
        Item(channel=item.channel, action="lista", title="Películas",
            url=url+"Todos", thumbnail=thumb_movies))
    itemlist.append(
        Item(channel=item.channel, action="letters", title="Listado alfabético",
            url=url, thumbnail=get_thumb("alphabet", auto=True)))
    itemlist.append(
        Item(channel=item.channel, action="years", title="Décadas",
            url=url, thumbnail=get_thumb("year", auto=True)))
    
    itemlist.append(Item(channel=item.channel, action="search", title="Buscar...",
            thumbnail=get_thumb("search", auto=True)))

    autoplay.show_option(item.channel, itemlist)
    return itemlist

def letters(item):
    logger.info()
    itemlist = []
    
    itemlist.append(
        Item(channel=item.channel, action="lista", title="0-9",
            url=item.url + "1", thumbnail=item.thumbnail))

    for letter in list(string.ascii_lowercase):
        itemlist.append(item.clone(action="lista", title=letter.upper(),
        url=item.url+letter.upper(), thumbnail=get_thumb("year", auto=True)))

    return itemlist

def years(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    match = soup.find("div", class_ = "widget-content list-label-widget-content")

    for year in match.find_all("li"):
        contains_digit = any(map(str.isdigit, str(year.a.text)))
        if contains_digit:
            itemlist.append(item.clone(action="lista", title=year.a.text,
                url=year.a["href"]))

    return itemlist

def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = host + "/search?q=" + texto
    
    if texto != '':
        return lista(item)
    else:
        return []

def lista(item):
    logger.info()
    itemlist = []
    
    soup = create_soup(item.url)
    matches = soup.find_all("div", class_= "post bar hentry")
    
    try:
        next_page = soup.find("a", class_="blog-pager-older-link")['href']
    except:
        next_page = None

    for elem in matches:
        logger.info(elem.find("h2"))
        scrapedurl = elem.find("h2").a["href"]
        scrapedthumbnail = elem.find("img")["src"]
        scrapedtitle = elem.find("h2").a.text
        if "Etiquetas" in elem.find("span").text:
            scrapedplot = elem.find("div", class_ = "entry")
        else:
            scrapedplot = elem.find("span").text

        scrapedyear = re.findall("\d*\.*\d+", scrapedtitle)
        year = [number for number in scrapedyear if len(number) == 4][0]
        title = scrapedtitle.split(" " + year)[0] 
        title = title[:-1]if ","==title[-1] else title

        infoLabels = {"year":year}

        context = autoplay.context

        itemlist.append(Item(channel=item.channel, title=title, url=scrapedurl,
            infoLabels = infoLabels, plot= scrapedplot, action="findvideos", thumbnail=scrapedthumbnail,
            contentTitle=title, context=context))

    if next_page and len(itemlist)>19:
        itemlist.append(
            Item(channel=item.channel, url=next_page, action="lista",
                title="[COLOR cyan]Página Siguiente >>[/COLOR]"))

    tmdb.set_infoLabels(itemlist)
    return itemlist

def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    soup = create_soup(item.url)

    url = soup.find("div", class_="post-body entry-content").find("iframe")["src"]
    itemlist.append(item.clone(url=url, action="play", title= "%s"))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    
    autoplay.start(itemlist, item)

    if item.category=="peliculas" and config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(Item(channel=item.channel, url=item.url, contentTitle=item.contentTitle,
            infoLabels= item.infoLabels, action="add_pelicula_to_library",
            title="[COLOR yellow]Añadir esta película a la videoteca[/COLOR]"))

    return itemlist