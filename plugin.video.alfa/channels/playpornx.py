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
import base64

IDIOMAS = {'vo': 'VO'}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['mangovideo']

host = "https://watchfreexxx.net/"  #pandamovie

def mainlist(item):
    itemlist = []

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, title="Peliculas", action="lista",
                         url = urlparse.urljoin(host, "category/porn-movies/")))
    itemlist.append(Item(channel=item.channel, title="Escenas", action="lista",
                         url = urlparse.urljoin(host, "category/xxx-scenes/")))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=host+'?s=',
                         thumbnail='https://s30.postimg.cc/pei7txpa9/buscar.png',
                         fanart='https://s30.postimg.cc/pei7txpa9/buscar.png'))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto
    try:
        if texto != '':
            item.extra = 'Buscar'
            return lista(item)
        else:
            return []
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def lista(item):
    logger.info()
    itemlist = []
    if item.url == '': item.url = host
    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    patron = '<a class="thumb" href="([^"]+)".*?'
    patron += 'data-src="([^"]+)".*?'
    patron += 'title="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for data_1, data_2, data_3 in matches:
        url = data_1
        thumbnail = data_2
        title = data_3
        itemlist.append(Item(channel=item.channel, action='findvideos', title=title, contentTitle = title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail))
    next_page = scrapertools.find_single_match(data, '<a class="next page-link" href="([^"]+)"')
    if next_page != '':
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page,
                                   thumbnail='https://s16.postimg.cc/9okdu7hhx/siguiente.png', extra=item.extra))
    return itemlist


def findvideos(item):
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|amp;|\s{2}|&nbsp;", "", data)
    patron = '- on ([^"]+)" href="([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedtitle,url in matches:
        itemlist.append(item.clone(action="play", title ="%s", contentTitle=item.title, url=url ))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language, list_quality)
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    return itemlist

