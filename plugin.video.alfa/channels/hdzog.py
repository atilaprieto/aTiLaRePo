# -*- coding: utf-8 -*-
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys
from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools

host = 'https://hdzog.com'

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/new/"))
    itemlist.append( Item(channel=item.channel, title="Popular" , action="lista", url=host + "/popular/"))
    itemlist.append( Item(channel=item.channel, title="Longitud" , action="lista", url=host + "/longest/"))
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/categories/"))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist

def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = host + "/search/?q=%s" % texto
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
    data = httptools.downloadpage(item.url).data
    data = scrapertools.find_single_match(data,'<ul class="cf">(.*?)</ul>')
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron = '<li>.*?<a href="([^"]+)".*?'
    patron += '<img class="thumb" src="([^"]+)" alt="([^"]+)".*?'
    patron += '<span class="videos-count">(\d+)</span>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,vidnum in matches:
        scrapedplot = ""
        
        url= scrapedurl + "?sortby=post_date"
        title = scrapedtitle + " \(" + vidnum + "\)"
        itemlist.append( Item(channel=item.channel, action="lista", title=scrapedtitle, url=url,
                              thumbnail=scrapedthumbnail, plot=scrapedplot) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = scrapertools.find_single_match(data,'<ul class="cf">(.*?)<h2>Advertisement</h2>')
    patron  = '<li>.*?<a href="([^"]+)".*?'
    patron += 'src="([^"]+)" alt="([^"]+)".*?'
    patron += '<span class="time">(.*?)</span>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,time  in matches:
        contentTitle = scrapedtitle
        title = "[COLOR yellow]" + time + "[/COLOR] " + scrapedtitle
        thumbnail = scrapedthumbnail
        plot = ""
        itemlist.append( Item(channel=item.channel, action="play", title=title, url=scrapedurl,
                               thumbnail=thumbnail, plot=plot, contentTitle = contentTitle))
    next_page = scrapertools.find_single_match(data,'<a href="([^"]+)" title="Next Page" data-page-num="\d+">Next page &raquo;</a>')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title="Página Siguiente >>", text_color="blue", url=next_page) )
    return itemlist


def play(item):
    headers = {'Referer': item.url}
    post_url = host+'/sn4diyux.php'
    data = httptools.downloadpage(item.url).data
    
    patron = 'pC3:\'([^\']+)\',.*?'
    patron += 'video_id: (\d+),'
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
