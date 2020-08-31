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

host = 'https://collectionofbestporn.com'


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone(title="Nuevos" , action="lista", url=host + "/most-recent"))
    itemlist.append(item.clone(title="Mas vistos" , action="lista", url=host + "/most-viewed/week"))
    itemlist.append(item.clone(title="Mejor valorado" , action="lista", url=host + "/top-rated/week"))
    itemlist.append(item.clone(title="Mas metraje" , action="lista", url=host + "/longest/week"))
    itemlist.append(item.clone(title="PornStar" , action="categorias", url=host + "/pornstars/?plikes=1"))

    itemlist.append(item.clone(title="Categorias" , action="categorias", url=host + "/channels/"))
    itemlist.append(item.clone(title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%s/search/%s" % (host,texto)
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
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_='video-item')
    for elem in matches:
        url = elem.a['href']
        title = elem.find('div', class_='title')
        if "pornstars/" in item.url:
            title = title.text.strip()
        else:
            title = title.a['title']
        thumbnail = elem.img['src']
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(item.clone(action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('li', class_='next')
    if next_page:
        next_page = next_page.a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
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
    matches = soup.find_all('div', class_='video-item')
    for elem in matches:
        url = elem.a['href']
        stitle = elem.find('div', class_='title').a['title']
        thumbnail = elem.img['src']
        stime = elem.find('span', class_='time').text.strip()
        quality = elem.find('span', class_='quality')
        if stime:
            title = "[COLOR yellow]%s[/COLOR] %s" % (stime,stitle)
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (stime,stitle)
        plot = ""
        itemlist.append(item.clone(action="play", title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('li', class_='next')
    if next_page:
        next_page = next_page.a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url).find('video', class_='video-js')
    matches = soup.find_all('source')
    for elem in matches:
        url = elem['src']
        title = elem['res']
        itemlist.append(item.clone(action="play", title=title, url=url))
        
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    soup = create_soup(item.url).find('video', class_='video-js')
    matches = soup.find_all('source')
    for elem in matches:
        url = elem['src']
        quality = elem['res']
        itemlist.append(['.mp4 %s' %quality, url])
    return itemlist
