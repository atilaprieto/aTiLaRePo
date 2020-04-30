# -*- coding: utf-8 -*-
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido

import re

from platformcode import config, logger
from core import scrapertools
from core import servertools
from core.item import Item
from core import httptools
from channels import filtertools
from channels import autoplay

IDIOMAS = {'vo': 'VO'}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['gounlimited']

host = 'http://sexgalaxy.net'

# UBIQFILE  falta jetload

def mainlist(item):
    logger.info()
    itemlist = []

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, title="Peliculas", action="lista", url=host + "/full-movies/"))
    itemlist.append(Item(channel=item.channel, title="Peliculas JAV", action="lista", url=host + "/jav-movies/"))
    itemlist.append(Item(channel=item.channel, title="Videos", action="lista", url=host + "/videos/"))
    itemlist.append(Item(channel=item.channel, title="Canales", action="categorias", url=host + "/videos/"))
    itemlist.append(Item(channel=item.channel, title="Categorias", action="categorias", url=host + "/videos/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url =  "%s/?s=%s&submit=Search" % (host, texto)
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    if "Categorias" in item.title:
        data = scrapertools.find_single_match(data, '>Popular Categories<(.*?)>Popular Paysites<')
    else:
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


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, timeout=3).data
    patron = '<article id="post-.*?'
    patron += '<a href="([^"]+)" rel="bookmark">([^<]+)<.*?'
    patron += '<img src="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        scrapedplot = ""
        if not "manyvids" in scrapedtitle:
            itemlist.append(Item(channel=item.channel, action="findvideos", title=scrapedtitle, contentTitle=scrapedtitle,
                             fanart=scrapedthumbnail, url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot))
    next_page = scrapertools.find_single_match(data, '"page-numbers current">.*?href="([^"]+)">')
    if next_page != "":
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page))
    return itemlist

# https://jetload.net/p/1RyPRu5MQx5y/20v9e2rpnlne.mp4

def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    links_data = scrapertools.find_single_match(data, '<span id="more-(.*?)</p>')
    patron = '<a href="([^"]+)"[^<]+>(?:<strong> |)Streaming'
    matches = re.compile(patron, re.DOTALL).findall(links_data)
    for url in matches:
        itemlist.append(Item(channel=item.channel, title='%s', url=url, action='play', language='VO',contentTitle = item.contentTitle))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda x: x.title % x.server)
    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language, list_quality)
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    return itemlist
