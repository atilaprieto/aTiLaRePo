# -*- coding: utf-8 -*-
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
list_servers = ['gounlimited']

host = 'http://sexgalaxy.net'

def mainlist(item):
    logger.info()
    itemlist = []

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, title="Peliculas", action="lista", url=host + "/full-movies/"))
    itemlist.append(Item(channel=item.channel, title="Videos", action="lista", url=host + "/new-releases/"))
    itemlist.append(Item(channel=item.channel, title="Canales", action="canales", url=host))
    itemlist.append(Item(channel=item.channel, title="Categorias", action="categorias", url=host))
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


def canales(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(host).data
    data = scrapertools.find_single_match(data, '>Popular Paysites<(.*?)</p>')
    patron = '<a href="([^"]+)">([^<]+)<'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedtitle = str(scrapedtitle)
        thumbnail = urlparse.urljoin(item.url, scrapedthumbnail)
        itemlist.append(Item(channel=item.channel, action="lista", title=scrapedtitle, url=scrapedurl,
                             thumbnail=scrapedthumbnail, plot=scrapedplot))
    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = scrapertools.find_single_match(data, '>Popular Categories<(.*?)>Popular Paysites<')
    patron = '<a href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedtitle = str(scrapedtitle)
        thumbnail = urlparse.urljoin(item.url, scrapedthumbnail)
        itemlist.append(Item(channel=item.channel, action="lista", title=scrapedtitle, url=scrapedurl,
                             thumbnail=scrapedthumbnail, plot=scrapedplot))
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron = '<div class="post-img small-post-img">.*?<a href="([^"]+)" title="([^"]+)">.*?<img src="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        scrapedplot = ""
        calidad = scrapertools.find_single_match(scrapedtitle, '\(.*?/(\w+)\)')
        if calidad:
            scrapedtitle = "[COLOR red]" + calidad + "[/COLOR] " + scrapedtitle
        if not "manyvids" in scrapedtitle:
            itemlist.append(Item(channel=item.channel, action="findvideos", title=scrapedtitle, contentTitle=scrapedtitle,
                             fanart=scrapedthumbnail, url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot))
    next_page = scrapertools.find_single_match(data, '<a class="next page-numbers" href="([^"]+)"')
    if next_page != "":
        itemlist.append(item.clone(action="lista", title="Página Siguiente >>", text_color="blue", url=next_page))
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    links_data = scrapertools.find_single_match(data, '>severeporn.com<(.*?)</div>')
    patron = '<a href="([^"]+)"[^<]+>Streaming'
    matches = re.compile(patron, re.DOTALL).findall(links_data)
    for url in matches:
        itemlist.append(Item(channel=item.channel, title='%s', url=url, action='play', language='VO',contentTitle = item.contentTitle))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda x: x.title % x.server)
    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    return itemlist
