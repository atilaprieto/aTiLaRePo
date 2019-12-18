# -*- coding: utf-8 -*-
#------------------------------------------------------------
import urlparse
import re

from platformcode import config, logger
from core import scrapertools
from core import servertools
from core.item import Item
from core import httptools
from bs4 import BeautifulSoup
from channels import filtertools
from channels import autoplay

IDIOMAS = {'vo': 'VO'}
list_language = IDIOMAS.values()
list_quality = []
list_servers = ['gounlimited']

host = 'https://www.porndish.com'

def mainlist(item):
    logger.info()
    itemlist = []

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append( Item(channel=item.channel, title="Nuevos" , action="lista", url=host))
    itemlist.append( Item(channel=item.channel, title="Canal" , action="sub_menu", url=host))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))

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


def sub_menu(item):
    logger.info()

    itemlist = list()
    itemlist.append( Item(channel=item.channel, title="Bangbros" , action="categorias", url=host, id="menu-item-62819"))
    itemlist.append( Item(channel=item.channel, title="Brazzers" , action="categorias", url=host, id="menu-item-817"))
    itemlist.append( Item(channel=item.channel, title="Mofos" , action="categorias", url=host, id="menu-item-1707"))
    itemlist.append( Item(channel=item.channel, title="Pornpros" , action="categorias", url=host, id="menu-item-3774"))
    itemlist.append( Item(channel=item.channel, title="Realitykings" , action="categorias", url=host, id="menu-item-844"))
    itemlist.append( Item(channel=item.channel, title="Sis Loves Me" , action="lista", url=host + "/videos4/sislovesme/"))
    itemlist.append( Item(channel=item.channel, title="Teamskeet" , action="categorias", url=host, id="menu-item-1713"))
    itemlist.append( Item(channel=item.channel, title="Networks" , action="categorias", url=host, id="menu-item-23036"))
    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url).find('li', id=item.id)
    matches = soup.find_all('li', class_='menu-item-object-category')
    for elem in matches:
        scrapedurl = elem.a['href']
        scrapedtitle = elem.a.text
        scrapedplot = ""
        scrapedurl = urlparse.urljoin(item.url,scrapedurl)
        scrapedthumbnail = ""
        itemlist.append( Item(channel=item.channel, action="lista", title=scrapedtitle, url=scrapedurl,
                              fanart=scrapedthumbnail, thumbnail=scrapedthumbnail , plot=scrapedplot) )
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


def lista(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('article', class_='entry-tpl-grid')
    for elem in matches:
        url = elem.a['href']
        stitle = elem.img['alt']
        thumbnail = elem.img['data-lazy-src']
        stime = elem.find('time', class_='entry-date').text
        stime =scrapertools.find_single_match(stime,'(\d+:\d+)')
        title = "[COLOR yellow]%s[/COLOR] %s" % (stime,stitle)
        plot = ""
        itemlist.append( Item(channel=item.channel, action="findvideos", title=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail, plot=plot, contentTitle = title))
    try:
        next_page = soup.find('a', class_='g1-delta g1-delta-1st next')['href']
    except:
        next_page = None
    if next_page:
        itemlist.append(Item(channel=item.channel, action="lista", title='Página Siguiente >>',
                             text_color="blue", url=next_page.strip()))
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url).find_all('iframe')
    for elem in soup:
        url = elem['src']
        itemlist.append(item.clone(action="play", title= "%s" , contentTitle=item.title, url=url)) 
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize()) 
    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    return itemlist

