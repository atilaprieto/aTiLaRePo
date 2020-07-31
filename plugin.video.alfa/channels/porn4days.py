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

host = 'http://porn4days.org/'


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone(title="Nuevos" , action="lista", url=host + "newest/page1"))
    itemlist.append(item.clone(title="Mas vistos" , action="lista", url=host + "popullar/page1"))
    itemlist.append(item.clone(title="PornStar" , action="categorias", url=host + "/actors/?sort=by_likes"))
    itemlist.append(item.clone(title="Canal" , action="canal", url=host + "paysitelist"))

    itemlist.append(item.clone(title="Categorias" , action="categorias", url=host + "tags"))
    itemlist.append(item.clone(title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/search/page1/?s=%s" % (host,texto)
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def canal(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_='col-lg-3')
    for elem in matches:
        url = elem.a['href']
        title = elem.a.text
        url = urlparse.urljoin(host,url)
        thumbnail = ""
        plot = ""
        itemlist.append(item.clone(action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_='col-lg-3')
    for elem in matches:
        url = elem.a['href']
        thumbnail = elem.img['src']
        title = elem.img['alt']
        url = urlparse.urljoin(host,url)
        thumbnail = urlparse.urljoin(host,thumbnail)
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
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_='col-lg-3')
    for elem in matches:
        url = elem.a['href']
        stitle = elem.img['alt']
        thumbnail = elem.img['src']
        stime = elem.find('div', class_='timer').text.strip()
        if stime:
            title = "[COLOR yellow]%s[/COLOR] %s" % (stime,stitle)
        url = urlparse.urljoin(host,url)
        thumbnail = urlparse.urljoin(host,thumbnail)
        plot = ""
        itemlist.append(item.clone(action="play", title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('li', class_='active').next_sibling
    if next_page:
        next_page = next_page.a['href']
        if "/?s=" in item.url and not"/search/" in next_page:      #   
            next_page = "/search%s" %next_page
        next_page = urlparse.urljoin(host,next_page)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def play(item):
    logger.info(item)
    itemlist = servertools.find_video_items(item.clone(url = item.url, contentTitle = item.title))
    return itemlist

