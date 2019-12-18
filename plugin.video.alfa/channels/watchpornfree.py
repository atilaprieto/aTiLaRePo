# -*- coding: utf-8 -*-
#------------------------------------------------------------
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

# https://playpornfree.org/    https://mangoporn.net/   https://watchfreexxx.net/   https://losporn.org/  https://xxxstreams.me/  https://speedporn.net/

host = 'https://watchpornfree.info'

def mainlist(item):
    logger.info("")
    itemlist = []

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append( Item(channel=item.channel, title="Videos" , action="lista", url=host + "/category/clips-scenes"))
    itemlist.append( Item(channel=item.channel, title="Peliculas" , action="lista", url=host))
    itemlist.append( Item(channel=item.channel, title="Parodia" , action="lista", url=host + "/category/parodies"))
    itemlist.append( Item(channel=item.channel, title="Canal" , action="categorias", url=host))
    itemlist.append( Item(channel=item.channel, title="Año" , action="categorias", url=host))
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def search(item, texto):
    logger.info("")
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
    logger.info("")
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    if item.title == "Canal":
        data = scrapertools.find_single_match(data,'Scenes</a></li>(.*?)</ul>')
    if item.title == "Año":
        data = scrapertools.find_single_match(data,'Year</a>(.*?)</ul>')
    if item.title == "Categorias":
        data = scrapertools.find_single_match(data,'>Categories</div>(.*?)</ul>')
    patron  = '<a href="([^"]+)".*?>([^"]+)</a></li>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle  in matches:
        scrapedplot = ""
        scrapedtitle = scrapedtitle
        scrapedthumbnail = ""
        itemlist.append( Item(channel=item.channel, action="lista", title=scrapedtitle, url=scrapedurl,
                              thumbnail=scrapedthumbnail, plot=scrapedplot) )
    return itemlist

def lista(item):
    logger.info("")
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron = '<article class="TPost B">.*?'
    patron += '<a href="([^"]+)">.*?'
    patron += 'src="([^"]+)".*?'
    patron += '<div class="Title">([^"]+)</div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        scrapedplot = ""
        itemlist.append( Item(channel=item.channel, action="findvideos", title=scrapedtitle, url=scrapedurl,
                              fanart=scrapedthumbnail, thumbnail=scrapedthumbnail, contentTitle=scrapedtitle, plot=scrapedplot) )
    next_page = scrapertools.find_single_match(data,'<a class="next page-numbers" href="([^"]+)">Next &raquo;</a>')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title="Página Siguiente >>", text_color="blue", url=next_page) )
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
        itemlist.append(Item(channel=item.channel, title='%s', url=url, action='play', language='VO',contentTitle = item.contentTitle))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda x: x.title % x.server)
    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    return itemlist
