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
    itemlist.append(item.clone(title="Nuevos" , action="lista", url=host + "/videos/"))
    itemlist.append(item.clone(title="Canal" , action="categorias", url=host + "/channels/"))
    itemlist.append(item.clone(title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
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
    matches = soup.find_all('div', class_='col-6')
    for elem in matches:
        url = elem.a['href']
        title = elem.find('div', class_='float-left').text.strip()
        cantidad = elem.find('div', class_='float-right')
        if cantidad:
            cantidad = cantidad.text.strip()
            title = "%s (%s)" % (title,cantidad)
        thumbnail = ""
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
    matches = soup.find_all('div', class_='article-post')
    for elem in matches:
        url = elem.a['href']
        thumbnail = elem.img['src']
        stitle = elem.img['title'].replace("&lpar;", "(").replace("&rpar;", ")")
        quality = elem.find('span', class_='hd-text-icon')
        if quality:
            title = "[COLOR red]HD[/COLOR] %s" % stitle
        plot = ""
        itemlist.append(item.clone(action="findvideos", title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('a', class_='next page-link')
    if next_page:
        next_page = next_page['href']
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    url = scrapertools.find_single_match(data, '<div class="video-container">.*?src="([^"]+)"')
    if "ultrahorny" in url:
        import base64
        data = httptools.downloadpage(url).data
        data = scrapertools.find_single_match(data, '<script>document.write\(atob\("([^"]+)"')
        data = data.replace("\\x", "").decode('hex')
        data = base64.b64decode(data)
        logger.debug(data)
        patron = 'file:"([^"]+)",label: "([^"]+)",'
        matches = re.compile(patron,re.DOTALL).findall(data)
        for url, quality in matches:
            itemlist.append(item.clone(action="play", title= quality, contentTitle = item.title, url=url))
    else:
        itemlist.append(item.clone(action="play", title=url, contentTitle = item.title, url=url))
    return itemlist[::-1]

def play(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(action="play", title= "%s", contentTitle = item.title, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist

