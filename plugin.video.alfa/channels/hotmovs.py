# -*- coding: utf-8 -*-
#------------------------------------------------------------

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                                             # Usamos el nativo de PY2 que es más rápido

import re
import os

from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools

host = 'https://hotmovs.com'

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(title="Nuevas" , action="lista", url=host + "/latest-updates/"))
    itemlist.append(item.clone(title="Mas Vistas" , action="lista", url=host + "/most-popular/?sort_by=video_viewed_week"))
    itemlist.append(item.clone(title="Mejor valorada" , action="lista", url=host + "/top-rated/?sort_by=rating_week"))
    itemlist.append(item.clone(title="Canal" , action="catalogo", url=host + "/channels/?sort_by=cs_viewed"))
    itemlist.append(item.clone(title="Pornstars" , action="categorias", url=host + "/models/"))
    itemlist.append(item.clone(title="Categorias" , action="categorias", url=host + "/categories/?sort_by=title"))
    itemlist.append(item.clone(title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "%20")
    item.url = "%s/search/?q=%s" % (host, texto)
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
    patron  = '<a class="thumbnail" href="([^"]+)">.*?'
    patron += '<img src="([^"]+)".*?'
    patron += '<span class="thumbnail__info__right">\s+([^"]+)\s+</span>.*?'
    patron += '<h5>([^"]+)</h5>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,cantidad,scrapedtitle in matches:
        scrapedplot = ""
        cantidad = cantidad.replace("         ", "")
        scrapedtitle = scrapedtitle + " (" + cantidad +")"
        scrapedurl = urlparse.urljoin(item.url,scrapedurl)
        itemlist.append(item.clone(action="lista", title=scrapedtitle, url=scrapedurl,
                              thumbnail=scrapedthumbnail , plot=scrapedplot) )
    next_page = scrapertools.find_single_match(data,'<li class="next"><a href="([^"]+)"')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="catalogo", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron  = '<a class="thumbnail" href="([^"]+)" title="([^"]+)">.*?'
    patron += '<img src="([^"]+)".*?'
    patron += '<i class="mdi mdi-video"></i>([^"]+)</div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,scrapedthumbnail,cantidad in matches:
        scrapedplot = ""
        cantidad = cantidad.replace("        ", "")
        scrapedtitle = scrapedtitle + " (" + cantidad +")"
        scrapedurl = urlparse.urljoin(item.url,scrapedurl)
        if "categories" in scrapedurl:
            scrapedurl += "/?sort_by=post_date"
        itemlist.append(item.clone(action="lista", title=scrapedtitle, url=scrapedurl,
                              thumbnail=scrapedthumbnail, plot=scrapedplot) )
    next_page = scrapertools.find_single_match(data,'<li class="next"><a href="([^"]+)"')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron = '<article class="item" data-video-id="\d+">.*?'
    patron += 'href="([^"]+)".*?'
    patron += 'src="([^"]+)" alt="([^"]+)".*?<div class="thumbnail__info__right">(.*?)</div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,scrapedtime  in matches:
        url = urlparse.urljoin(item.url,scrapedurl)
        title = "[COLOR yellow]" + scrapedtime + "[/COLOR] " + scrapedtitle
        thumbnail = scrapedthumbnail
        plot = ""
        itemlist.append(item.clone(action="play", title=title, url=url, thumbnail=thumbnail,
                              plot=plot, contentTitle = title))
    next_page = scrapertools.find_single_match(data,'<li class="next"><a href="([^"]+)"')
    if "#" in next_page:
        next_page = scrapertools.find_single_match(data,'data-query="([^"]+)"><i class="mdi mdi-arrow-right">')
        next_page = next_page.replace(":", "=").replace(";", "&").replace("+from_albums", "")
        if "&" in item.url:
            item.url = scrapertools.find_single_match(item.url, '(.*?)&')
        next_page = "%s&%s" % (item.url, next_page)
    if not next_page.startswith("https"):
        next_page = urlparse.urljoin(item.url,next_page)
    itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def play(item):
    headers = {'Referer': item.url}
    post_url = host+'/sn4diyux.php'

    data = httptools.downloadpage(item.url).data
    patron = 'pC3:\'([^\']+)\',.*?'
    patron += '"video_id": (\d+),'
    info_b, info_a = scrapertools.find_single_match(data, patron)
    post = 'param=%s,%s' % (info_a, info_b)
    new_data = httptools.downloadpage(post_url, post=post, headers=headers).data
    texto = scrapertools.find_single_match(new_data, 'video_url":"([^"]+)"')
    url = dec_url(texto)
    item.url = httptools.downloadpage(url, only_headers=True).url
    
    return [item]


def dec_url(txt):
    #truco del mendrugo
    if PY3:
        txt = txt.encode().decode('unicode-escape')
    else:
        txt = txt.decode('unicode-escape').encode('utf8')
    txt = txt.replace('А', 'A').replace('В', 'B').replace('С', 'C').replace('Е', 'E').replace('М', 'M').replace('~', '=').replace(',','/')
    logger.error(txt)
    import base64
    url = base64.b64decode(txt)
    return url

