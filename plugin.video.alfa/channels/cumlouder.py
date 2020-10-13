# -*- coding: utf-8 -*-
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido

import re

from core import httptools
from core import scrapertools
from core.item import Item
from platformcode import config, logger


host = 'https://www.cumlouder.com'

def mainlist(item):
    logger.info()
    itemlist = []
    config.set_setting("url_error", False, "cumlouder")
    itemlist.append(item.clone(title="Clips", action="lista", url= host + "/porn/"))
    itemlist.append(item.clone(title="Últimos videos", action="lista", url= host + "/2/?s=last"))
    itemlist.append(item.clone(title="Pornstars", action="pornstars_list", url=host + "/girls/"))
    itemlist.append(item.clone(title="Listas", action="series", url= host + "/series/"))
    itemlist.append(item.clone(title="Canal", action="pornstars_list", url=host + "/channels/"))
    itemlist.append(item.clone(title="Categorias", action="categorias", url= host + "/categories/"))
    itemlist.append(item.clone(title="Buscar", action="search", url= host + "/search?q=%s"))
    return itemlist


def search(item, texto):
    logger.info()
    item.url = item.url % texto
    item.action = "lista"
    try:
        return lista(item)
    except:
        import traceback
        logger.error(traceback.format_exc())
        return []


def pornstars_list(item):
    logger.info()
    itemlist = []
    if "/channels/" in item.url:
        itemlist.append(item.clone(title="Mas Populares", action="pornstars", url=host + "/channels/1/"))
    else:
        itemlist.append(item.clone(title="Mas Populares", action="pornstars", url=host + "/girls/1/"))
    for letra in "abcdefghijklmnopqrstuvwxyz":
        itemlist.append(item.clone(title=letra.upper(), url=urlparse.urljoin(item.url, letra), action="pornstars"))
    return itemlist


def pornstars(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    if "/channels/" in item.url:
        patron = '<a channel-url=.*?href="([^"]+)".*?'
    else:
        patron = '<a girl-url=.*?href="([^"]+)".*?'
    patron += 'data-src="([^"]+)".*?alt="([^"]+)".*?'
    patron += '<span class="ico-videos sprite"></span>([^<]+)</span>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    
    for url, thumbnail, title, count in matches:
        
        if "go.php?" in url:
            url = urllib.unquote(url.split("/go.php?u=")[1].split("&")[0])
            thumbnail = urllib.unquote(thumbnail.split("/go.php?u=")[1].split("&")[0])
        else:
            url = urlparse.urljoin(item.url, url)
            if not thumbnail.startswith("https"):
                thumbnail = "https:%s" % thumbnail
        
        itemlist.append(item.clone(title="%s (%s)" % (title, count.strip()), url=url, 
                        action="lista", fanart=thumbnail, thumbnail=thumbnail))
    # Paginador
    next_page = scrapertools.find_single_match(data,'<a class="btn-pagination" itemprop="name" href="([^"]+)">Next')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="pornstars", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron = '<a tag-url=.*?'
    patron += 'href="([^"]+)".*?'
    patron += 'data-src="([^"]+)".*?alt="([^"]+)".*?'
    patron += '<span class="cantidad">([^<]+)</span>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for url, thumbnail, title, count in matches:
        title="%s (%s)" % (title, count.strip())
        if "go.php?" in url:
            url = urllib.unquote(url.split("/go.php?u=")[1].split("&")[0])
            thumbnail = urllib.unquote(thumbnail.split("/go.php?u=")[1].split("&")[0])
        else:
            url = urlparse.urljoin(item.url, url)
            if not thumbnail.startswith("https"):
                thumbnail = "https:%s" % thumbnail
        itemlist.append(item.clone(action="lista", title=title, url=url, fanart=thumbnail, thumbnail=thumbnail))
    # Paginador
    next_page = scrapertools.find_single_match(data,'<a class="btn-pagination" itemprop="name" href="([^"]+)">Next')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def series(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron = '<a onclick=.*?href="([^"]+)".*?'
    patron += 'data-src="([^"]+)".*?'
    patron += 'h2 itemprop="name">([^<]+).*?'
    patron += 'p>([^<]+)</p>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for url, thumbnail, title, count in matches:
        title="%s (%s) " % (title, count)
        url=urlparse.urljoin(item.url, url)
        itemlist.append(item.clone(title=title, url=url, action="lista", fanart=thumbnail, thumbnail=thumbnail))
    # Paginador
    next_page = scrapertools.find_single_match(data,'<a class="btn-pagination" itemprop="name" href="([^"]+)">Next')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="series", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron = '<a class="muestra-escena" href="([^"]+)".*?'
    patron += 'data-src="([^"]+)".*?alt="([^"]+)".*?'
    patron += '"ico-minutos sprite"></span>([^<]+)</span>(.*?)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for url, thumbnail, title, duration,calidad in matches:
        if "hd sprite" in calidad:
            title="[COLOR yellow]%s[/COLOR]  [COLOR red]HD[/COLOR] %s" % (duration.strip(),  title)
        else:
            title="[COLOR yellow]%s[/COLOR] %s" % (duration.strip(), title)
        if "go.php?" in url:
            url = urllib.unquote(url.split("/go.php?u=")[1].split("&")[0])
            thumbnail = urllib.unquote(thumbnail.split("/go.php?u=")[1].split("&")[0])
        else:
            url = urlparse.urljoin(host, url)
            if not thumbnail.startswith("https"):
                thumbnail = "https:%s" % thumbnail
        itemlist.append(item.clone(title=title, url=url,
                                   action="play", thumbnail=thumbnail, contentThumbnail=thumbnail,
                                   fanart=thumbnail, contentType="movie", contentTitle=title))
    # Paginador
    next_page = scrapertools.find_single_match(data,'<a class="btn-pagination" itemprop="name" href="([^"]+)">Next')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron = '<source src="([^"]+)" type=\'video/([^\']+)\' label=\'[^\']+\' res=\'([^\']+)\''
    url, type, res = re.compile(patron, re.DOTALL).findall(data)[0]
    if "go.php?" in url:
        url = urllib.unquote(url.split("/go.php?u=")[1].split("&")[0])
    elif not url.startswith("http"):
        url = "https:%s" % url.replace("&amp;", "&")
    title="Video %s" % res
    url = url.replace("amp;", "")
    itemlist.append(item.clone(action="play", title=title, contentTitle=item.contentTitle, url=url, server="directo"))
    return itemlist
