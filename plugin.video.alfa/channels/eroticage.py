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
from core import servertools
from core.item import Item
from core import httptools
from channels import filtertools
from channels import autoplay
from bs4 import BeautifulSoup


IDIOMAS = {'vo': 'VO'}
list_language = IDIOMAS.values()
list_quality = []
list_servers = ['pornhub']

host = 'http://www.eroticage.net'


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(title="Novedades" , action="lista", url=host + "/?filter=latest"))
    itemlist.append(item.clone(title="Mas Popular" , action="lista", url=host + "/?filter=popular"))
    itemlist.append(item.clone(title="Mas Visto" , action="lista", url=host + "/?filter=most-viewed"))
    itemlist.append(item.clone(title="Mas Largo" , action="lista", url=host + "/?filter=longest"))
    itemlist.append(item.clone(title="Categorias" , action="categorias", url=host))
    itemlist.append(item.clone(title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/?s=%s" % (host, texto)
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
    matches = soup.find('div', class_='tagcloud').find_all('a', class_='tag-cloud-link')
    for elem in matches:
        url = elem['href']
        title = elem.text
        itemlist.append(item.clone(action="lista", title=title, url=url, thumbnail="", plot="") )
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
    if "/?s=" in item.url:
        matches = soup.find('section', class_='content-area with-sidebar-right').find_all('article', class_='thumb-block')
    else:
        matches = soup.find('div', class_='content-area with-sidebar-right').find_all('article', class_='thumb-block')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = scrapertools.find_single_match(str(elem), '.*?src="(.*?.(?:jpg|webp|png))"')
        time = elem.find('span', class_='duration')
        if time:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time.text,title)
        plot = ""
        itemlist.append(item.clone(action="play", title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('a', class_='current').parent.find_next_siblings("li")
    if next_page:
        next_page = next_page[0].a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_='responsive-player')
    for elem in matches:
        scrapedurl = elem.iframe['src']
        if "cine-matik.com" in scrapedurl:
            n = "yandex"
            m = scrapedurl.replace("https://cine-matik.com/player/play.php?", "")
            post = "%s&alternative=%s" %(m,n)
            headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
            data1 = httptools.downloadpage("https://cine-matik.com/player/ajax_sources.php", post=post, headers=headers).data
            if data1=="":
                n = "blogger"
                m = scrapedurl.replace("https://cine-matik.com/player/play.php?", "")
                post = "%s&alternative=%s" %(m,n)
                headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
                data1 = httptools.downloadpage("https://cine-matik.com/player/ajax_sources.php", post=post, headers=headers).data
            scrapedurl = scrapertools.find_single_match(data1,'"file":"([^"]+)"')
            if not scrapedurl:
                n = scrapertools.find_single_match(data1,'"alternative":"([^"]+)"')
                post = "%s&alternative=%s" %(m,n)
                headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
                data1 = httptools.downloadpage("https://cine-matik.com/player/ajax_sources.php", post=post, headers=headers).data
                scrapedurl = scrapertools.find_single_match(data1,'"file":"([^"]+)"')
            scrapedurl = scrapedurl.replace("\/", "/")
        if not "meta" in scrapedurl:
            itemlist.append(item.clone(action="play", title= "%s", contentTitle= item.title, url=scrapedurl))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
