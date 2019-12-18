# -*- coding: utf-8 -*-
# ------------------------------------------------------------
import urlparse
import re

from platformcode import config, logger
from core import scrapertools
from core import servertools
from core.item import Item
from core import httptools
from channels import filtertools
from channels import autoplay

IDIOMAS = {'vo': 'VO'}
list_language = IDIOMAS.values()
list_quality = []
list_servers = ['mangovideo']


host = 'https://pandamovies.pw'

def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Peliculas", action="lista", url=host + "/movies"))
    itemlist.append(Item(channel=item.channel, title="Canal", action="categorias", url=host + "/movies"))
    itemlist.append(Item(channel=item.channel, title="Categorias", action="categorias", url=host + "/movies"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = host + "/?s=%s" % texto
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def categorias(item):
    itemlist = []
    data = httptools.downloadpage(item.url).data
    if item.title == "Categorias":
        data = scrapertools.find_single_match(data, '<a href="#">Genres</a>(.*?)</ul>')
    else:
        data = scrapertools.find_single_match(data, '<a href="#">Studios</a>(.*?)</ul>')
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron = '<a href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedurl = scrapedurl.replace("https:", "")
        scrapedurl = "https:" + scrapedurl
        itemlist.append(Item(channel=item.channel, action="lista", title=scrapedtitle, url=scrapedurl,
                             thumbnail=scrapedthumbnail, plot=scrapedplot))
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron = '<div data-movie-id="\d+".*?'
    patron += '<a href="([^"]+)".*?oldtitle="([^"]+)".*?'
    patron += '<img data-original="([^"]+)".*?'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        url = urlparse.urljoin(item.url, scrapedurl)
        title = scrapedtitle
        thumbnail = scrapedthumbnail
        plot = ""
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=thumbnail,
                             fanart=thumbnail, plot=plot, contentTitle=title))
    next_page = scrapertools.find_single_match(data, '<li class=\'active\'>.*?href=\'([^\']+)\'>')
    if next_page == "":
        next_page = scrapertools.find_single_match(data, '<a.*?href="([^"]+)" >Next &raquo;</a>')
    if next_page != "":
        next_page = urlparse.urljoin(item.url, next_page)
        itemlist.append(item.clone(action="lista", title="Página Siguiente >>", text_color="blue", url=next_page))
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    links_data = scrapertools.find_single_match(data, '<div id="pettabs">(.*?)</ul>')
    patron = 'href="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(links_data)
    for url in matches:
        url = url.replace("/waaws.tk/", "/netu.tv/") 
        itemlist.append(Item(channel=item.channel, title='%s', url=url, action='play', language='VO',contentTitle = item.contentTitle))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda x: x.title % x.server)
    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    return itemlist
