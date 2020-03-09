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

from core import httptools
from core import scrapertools
from core import servertools
from core.item import Item
from platformcode import logger

host = 'https://es.redtube.com'

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Nuevas" , action="lista", url=host + "/newest"))
    itemlist.append( Item(channel=item.channel, title="Mas Vistas" , action="lista", url=host + "/mostviewed"))
    itemlist.append( Item(channel=item.channel, title="Mejor valorada" , action="lista", url=host + "/top"))
    itemlist.append( Item(channel=item.channel, title="Pornstars" , action="catalogo", url=host + "/pornstar"))
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/categories/popular"))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/?search=%s" % (host, texto)
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def catalogo(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    data = scrapertools.find_single_match(data,'<ul id="recommended_pornstars_block"(.*?)<div id="footer_container">')
    patron  = '<a class="pornstar_link js_mpop js-pop".*?'
    patron  = 'href="([^"]+)".*?'
    patron += 'data-src = "([^"]+)".*?'
    patron += 'title="([^"]+)".*?'
    patron += '<div class="ps_info_count">\s+(\d+)\s+Videos'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,cantidad in matches:
        scrapedplot = ""
        scrapedtitle = "%s (%s)" %(scrapedtitle, cantidad)
        scrapedurl = urlparse.urljoin(item.url,scrapedurl)
        itemlist.append( Item(channel=item.channel, action="lista", title=scrapedtitle, url=scrapedurl,
                              fanart=scrapedthumbnail, thumbnail=scrapedthumbnail, plot=scrapedplot) )
    next_page_url = scrapertools.find_single_match(data,'<a id="wp_navNext".*?href="([^"]+)">')
    if next_page_url!="":
        next_page_url = urlparse.urljoin(item.url,next_page_url)
        itemlist.append(item.clone(action="catalogo", title="Página Siguiente >>", text_color="blue", url=next_page_url) )
    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron = '<li id="categories_list_block_.*?'
    patron += '<a href="([^"]+)".*?'
    patron += 'data-src="([^"]+)".*?'
    patron += 'alt="([^"]+)".*?'
    patron += '_count">([^"]+) Videos'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,cantidad in matches:
        scrapedplot = ""
        cantidad = cantidad.strip()
        scrapedtitle = "%s (%s)" %(scrapedtitle, cantidad)
        scrapedurl = urlparse.urljoin(item.url,scrapedurl)
        itemlist.append( Item(channel=item.channel, action="lista", title=scrapedtitle, url=scrapedurl,
                              fanart=scrapedthumbnail, thumbnail=scrapedthumbnail, plot=scrapedplot) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = scrapertools.find_single_match(data,'Eliminar anuncios(.*?)Eliminar anuncios')
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron = 'data-src="([^"]+)".*?'
    patron += '<span class="duration">(.*?)</a>.*?'
    patron += '<a title="([^"]+)".*?href="(/\d+)"' #purga los premium y yourporn
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedthumbnail,duration,scrapedtitle,scrapedurl in matches:
        url = urlparse.urljoin(item.url,scrapedurl)
        scrapedhd = scrapertools.find_single_match(duration, '<span class=".*?">([^<]+)</span>')
        if scrapedhd:
            duration = scrapertools.find_single_match(duration, '</span>([^<]+)</span>').strip()
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]%s[/COLOR] %s" % (duration, scrapedhd ,scrapedtitle)
        else:
            duration = scrapertools.find_single_match(duration, '([^<]+)</span>').strip()
            title = "[COLOR yellow]%s[/COLOR] %s" % (duration, scrapedtitle)
        scrapedthumbnail = scrapedthumbnail.replace("{index}.", "1.")
        plot = ""
        itemlist.append( Item(channel=item.channel, action="play" , title=title , url=url,
                              fanart=scrapedthumbnail, thumbnail=scrapedthumbnail, plot=plot, contentTitle = title) )
    next_page_url = scrapertools.find_single_match(data,'<a id="wp_navNext".*?href="([^"]+)">').replace("amp;", "")
    if next_page_url!="":
        next_page_url = urlparse.urljoin(item.url,next_page_url)
        itemlist.append(item.clone(action="lista", title="Página Siguiente >>", text_color="blue", url=next_page_url) )
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    url = item.url
    itemlist.append(item.clone(action="play", title= "%s", contentTitle= item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist

