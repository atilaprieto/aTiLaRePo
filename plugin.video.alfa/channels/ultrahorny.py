# -*- coding: utf-8 -*-
#------------------------------------------------------------
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
from core.item import Item
from core import servertools
from core import httptools
from bs4 import BeautifulSoup

host = 'https://ultrahorny.com'


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(title="Nuevos" , action="lista", url=host))
    itemlist.append(item.clone(title="Canal" , action="categorias", url=host))
    # itemlist.append(item.clone(title="Pornstars" , action="categorias", url=host + "/pornstar/?filter=popular"))  #no tiene contenido
    itemlist.append(item.clone(title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s//?s=%s" % (host,texto)
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
    soup = create_soup(item.url).find('ul', class_='lst_categorias') 
    matches = soup.find_all('li')
    for elem in matches:
        url = elem.a['href']
        thumbnail = elem.img['src']
        title = elem.find('h5')
        if title:
            title = title.text.strip()
        else:
            title = elem.find('h3').text.strip() #para pornstars
        cantidad = elem.find('div', class_='float-right')
        if cantidad:
            cantidad = cantidad.text.strip()
            title = "%s (%s)" % (title,cantidad)
        plot = ""
        itemlist.append(item.clone(action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
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
    if "/?s=" in item.url or "/channel/" in item.url:
        soup = create_soup(item.url)
    else:
        soup = create_soup(item.url).find("div", id="widget_post-2")
    matches = soup.find_all('article', class_='post_not')
    for elem in matches:
        url = elem.a['href']
        thumbnail = elem.img['src']
        title = elem.img['alt'].replace("&lpar;", "(").replace("&rpar;", ")")
        quality = elem.find('span', class_='hd-text-icon')
        if quality:
            title = "[COLOR red]HD[/COLOR] %s" % title
        plot = ""
        itemlist.append(item.clone(action="play", title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('a', class_='page-link current')
    if next_page:
        next_page = next_page.find_next('a')['href']
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_='cnt_post video_cnt')
    for elem in matches:
        url = elem.iframe['src']
        if "pornoflix" in url:
            url = create_soup(url).find('source')['src']
    itemlist.append(item.clone(action="play", title=url, contentTitle = item.title, url=url))
    return itemlist

def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_='cnt_post video_cnt')
    for elem in matches:
        url = elem.iframe['src']
        if "pornoflix" in url:
            url = create_soup(url).find('source')['src']
        itemlist.append(item.clone(action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist

