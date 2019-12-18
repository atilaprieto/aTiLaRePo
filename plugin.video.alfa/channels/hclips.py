# -*- coding: utf-8 -*-
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys
from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools

host = 'https://hclips.com'


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Nuevos" , action="peliculas", url=host + "/latest-updates/"))
    itemlist.append( Item(channel=item.channel, title="Popular" , action="peliculas", url=host + "/most-popular/?"))
    itemlist.append( Item(channel=item.channel, title="Longitud" , action="peliculas", url=host + "/longest/?"))
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/categories/"))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = host + "/search/?q=%s" % texto
    try:
        return peliculas(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron  = '<a href="([^"]+)" class="thumb">.*?'
    patron += 'src="([^"]+)".*?'
    patron += '<strong class="title">([^"]+)</strong>.*?'
    patron += '<b>(.*?)</b>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,vidnum in matches:
        scrapedplot = ""
        title = scrapedtitle + " \(" + vidnum + "\)"
        itemlist.append( Item(channel=item.channel, action="peliculas", title=scrapedtitle, url=scrapedurl,
                               thumbnail=scrapedthumbnail, plot=scrapedplot) )
    return itemlist


def peliculas(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron  = '<a href="([^"]+)" class="thumb">.*?'
    patron += '<img src="([^"]+)" alt="([^"]+)".*?'
    patron += '<span class="dur">(.*?)</span>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,time  in matches:
        title = "[COLOR yellow]" + time + "[/COLOR] " + scrapedtitle
        contentTitle = title
        thumbnail = scrapedthumbnail
        plot = ""
        itemlist.append( Item(channel=item.channel, action="play", title=title, url=scrapedurl,
                              thumbnail=thumbnail, plot=plot, contentTitle = contentTitle))
    next_page_url = scrapertools.find_single_match(data,'<a href="([^"]+)" title="Next Page">Next</a>')
    if next_page_url!="":
        next_page_url = urlparse.urljoin(item.url,next_page_url)
        itemlist.append(item.clone(action="peliculas", title="Página Siguiente >>", text_color="blue", url=next_page_url) )
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
    txt = txt.decode('unicode-escape').encode('utf8')
    txt = txt.replace('А', 'A').replace('В', 'B').replace('С', 'C').replace('Е', 'E').replace('М', 'M').replace('~', '=').replace(',','/')
    import base64
    url = base64.b64decode(txt)
    return url

