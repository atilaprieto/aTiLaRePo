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

host = 'https://www.joysporn.com/'


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(title="Nuevos" , action="lista", url=host))
    itemlist.append(item.clone(title="Mas vistos" , action="lista", url=host + "/most-popular/"))
    itemlist.append(item.clone(title="Mejor valorado" , action="lista", url=host + "/top-rated/"))
    itemlist.append(item.clone(title="Categorias" , action="categorias", url=host + "/categories.html"))
    itemlist.append(item.clone(title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/index.php?do=search&subaction=search&story=%s&search_start=1" % (host,texto)
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
    matches = soup.find('div', class_='porncategories').find_all('a')
    for elem in matches:
        url = elem['href']
        thumbnail = elem.img['src']
        title = elem.find('h2').text
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
    matches = soup.find_all('div', class_='video_c')
    for elem in matches:
        url = elem.a['href']
        stitle = elem.find('h2').text.strip()
        thumbnail = elem.img['src']
        stime = elem.find('div', class_='vidduration').text.strip()
        if stime:
            title = "[COLOR yellow]%s[/COLOR] %s" % (stime,stitle)
        plot = ""
        itemlist.append(item.clone(action="play", title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('div', class_='navigation').span.find_next_siblings("a")
    if next_page:
        next_page = next_page[0]
        if "/index.php?do=search" in item.url:
            prev_page = scrapertools.find_single_match(item.url, "(.*?&search_start=)")
            next_page = next_page.text
            next_page = prev_page + next_page
        else:
            next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('div', id='player')
    for elem in matches:
        url = elem['data-q']
        id = elem['data-id']
        id1 = int(id) // 1000 *1000
        server = elem['data-n']
        url = url.split(",")
        a = len(url)-1
        for elem in url:
            elem = elem.split(";")
            quality = elem[0]
            s1= elem[-2]
            s2 = elem[-1]
            url = "https://s%s.fapmedia.com/cqpvid/%s/%s/%s/%s/%s_%s.mp4" %(server,s1,s2,id1,id,id,quality)
            url = url.replace("_720p", "") 
            itemlist.append(item.clone(action="play", title= ".mp4 %s" %quality, contentTitle = item.title, url=url))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('div', id='player')
    for elem in matches:
        url = elem['data-q']
        id = elem['data-id']
        id1 = int(id) // 1000 *1000
        server = elem['data-n']
        url = url.split(",")
        a = len(url)-1
        for elem in url:
            elem = elem.split(";")
            quality = elem[0]
            s1= elem[-2]
            s2 = elem[-1]
            url = "https://s%s.fapmedia.com/cqpvid/%s/%s/%s/%s/%s_%s.mp4" %(server,s1,s2,id1,id,id,quality)
            url = url.replace("_720p", "")
            itemlist.append(['.mp4 %s' %quality, url])
    return itemlist

