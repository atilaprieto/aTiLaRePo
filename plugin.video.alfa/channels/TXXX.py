# -*- coding: utf-8 -*-
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys
from core import scrapertools
from core import servertools
from core.item import Item
from platformcode import config, logger
from core import httptools

host = 'https://txxx.com'


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Ultimas" , action="lista", url=host + "/latest-updates/"))
    itemlist.append( Item(channel=item.channel, title="Mejor valoradas" , action="lista", url=host + "/top-rated/"))
    itemlist.append( Item(channel=item.channel, title="Mas popular" , action="lista", url=host + "/most-popular/"))
    itemlist.append( Item(channel=item.channel, title="Canal" , action="catalogo", url=host + "/channels-list/most-popular/"))
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/categories/"))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = host + "/search/s=%s" % texto
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
    patron = '<div class="channel-thumb">.*?'
    patron += '<a href="([^"]+)" title="([^"]+)".*?'
    patron += '<img src="([^"]+)".*?'
    patron += '<span>(.*?)</span>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,scrapedthumbnail,num in matches:
        scrapedplot = ""
        scrapedurl = host + scrapedurl
        title = scrapedtitle + "[COLOR yellow]  " + num + "[/COLOR]"
        itemlist.append( Item(channel=item.channel, action="lista", title=title , url=scrapedurl , 
                        thumbnail=scrapedthumbnail , plot=scrapedplot) )
    next_page = scrapertools.find_single_match(data,'<a class=" btn btn--size--l btn--next" href="([^"]+)" title="Next Page"')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append( Item(channel=item.channel , action="catalogo" , title="Página Siguiente >>" , 
                        text_color="blue", url=next_page) )
    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron = '<a class="categories-list__link" href="([^"]+)">.*?'
    patron += '<span class="categories-list__name cat-icon" data-title="([^"]+)">.*?'
    patron += '<span class="categories-list__badge">(.*?)</span>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,num in matches:
        url = urlparse.urljoin(item.url,scrapedurl)
        scrapedthumbnail = ""
        scrapedplot = ""
        title = scrapedtitle + "[COLOR yellow]  " + num + "[/COLOR]"
        itemlist.append( Item(channel=item.channel, action="lista", title=title , url=url , 
                        thumbnail=scrapedthumbnail, plot=scrapedplot) )
    return  sorted(itemlist, key=lambda i: i.title)


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron = 'class="thumb__aspect">.*?\'(.*?)\'.*?'
    patron += '</a>(.*?)</div>.*?href="([^"]+)">([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedthumbnail, scrapedtime, scrapedurl, scrapedtitle in matches:
        scrapedurl = urlparse.urljoin(host,scrapedurl)
        contentTitle = scrapedtitle
        scrapedhd = scrapertools.find_single_match(scrapedtime, '<span class="thumb__hd">(.*?)</span>')
        duration = scrapertools.find_single_match(scrapedtime, '<span class="thumb__duration">(.*?)</span>')
        if scrapedhd != '':
            title = "[COLOR yellow]" +duration+ "[/COLOR] " + "[COLOR tomato][" +scrapedhd+ "][/COLOR] "+scrapedtitle
        else:
            title = "[COLOR yellow]" + duration + "[/COLOR] " + scrapedtitle
        thumbnail = scrapedthumbnail
        plot = ""
        itemlist.append( Item(channel=item.channel, action="play" , title=title , url=scrapedurl, thumbnail=thumbnail, 
                        plot=plot, contentTitle=title) )
    next_page = scrapertools.find_single_match(data,'<a class="paginator__item paginator__item--next paginator__item--arrow" href="([^"]+)"')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title="Página Siguiente >>", text_color="blue", url=next_page) )
    return itemlist


def play(item):
    headers = {'Referer': item.url}
    post_url = host+'/sn4diyux.php'
    
    data = httptools.downloadpage(item.url).data
    patron = "pC3:'([^']+)',video_id: (\d+),"
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

