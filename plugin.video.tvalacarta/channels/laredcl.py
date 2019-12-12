# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para La Red (Chile)
# creado por rsantaella
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "laredcl"
__title__ = "laredcl"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.laredcl mainlist")

    itemlist = []
    
    item.url="http://lared.cl/programas"
    itemlist.extend(programas(item))
    
    item.url="http://lared.cl/archivo-programas"
    itemlist.extend(programas(item))

    return itemlist

def programas(item):
    logger.info("tvalacarta.channels.laredcl programas")    

    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    '''
    <section class="block-items">
    <div class="title rojo">
    <a href="http://lared.cl/programas/mentiras-verdaderas"><strong>Mentiras Verdaderas</strong
    '''
    patron  = '<section class="block-items"[^<]+'
    patron += '<div class="title[^<]+'
    patron += '<a href="([^"]+)">(.*?)</a'

    matches = re.compile(patron,re.DOTALL).findall(data)
    
    for scrapedurl,scrapedtitle in matches:
        thumbnail = ""
        url = urlparse.urljoin(item.url,scrapedurl)
        title = scrapertools.htmlclean(scrapedtitle)
        plot = ""

        itemlist.append( Item(channel=__channel__, action="episodios", title=title, show=title, url=url, thumbnail=thumbnail,  plot=plot, folder=True))

    return itemlist

def detalle_programa(item):
    return item

def episodios(item):
    logger.info("tvalacarta.channels.laredcl episodios")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)    
    #<div class="lr-title">Programas <strong>Completos</strong></div> <a href="http://lared.cl/category/programas/hola-chile/programas-completos-holachile">Ver todos</a>
    url = scrapertools.find_single_match(data,'<div class="lr-title">Programas <strong>Completos</strong></div> <a href="([^"]+)"')
    if url!="":
        data = scrapertools.cachePage(url)

    '''
    <div class="items-list-bg">
    <div class="item" style="background: url(http://static.lared.cl/wp-content/uploads/2017/11/28150638/2017-11-28T10_00_15.511Z_image-365x235.jpg) no-repeat center center; -webkit-background-size: cover; -moz-background-size: cover; -o-background-size: cover; background-size: cover;"> 
    <a href="http://lared.cl/2017/programas/hola-chile/hola-chile-programa-completo-martes-28-de-noviembre-2017">
    <h2>Hola Chile Programa Completo Martes 28 de Noviembre 2017
    </h2> <span class="overlay"></span> </a></div>
    '''

    patron = '<div class="item" style="background. url\(([^\)]*)\)[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<h2>([^<]+)<'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedthumbnail,scrapedurl,scrapedtitle in matches:
        title = scrapedtitle
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        url = urlparse.urljoin(item.url,scrapedurl)
        plot = ""
        itemlist.append( Item(channel=__channel__, action="play", title=title, url=url, thumbnail=thumbnail, plot=plot, show=item.show, folder=False))

    next_page_url = scrapertools.find_single_match(data,'<a class="nextpostslink" rel="next" href="([^"]+)">')
    if next_page_url!="":
        itemlist.append( Item(channel=__channel__, title=">> Página siguiente" , action="episodios" , url=urlparse.urljoin(item.url,next_page_url), show=item.show) )

    return itemlist

def detalle_episodio(item):

    data = scrapertools.cache_page(item.url)

    item.plot = scrapertools.htmlclean(scrapertools.find_single_match(data,'<meta content="([^"]+)" itemprop="description')).strip()
    item.thumbnail = scrapertools.find_single_match(data,'<meta content="([^"]+)" itemprop="thumbnailUrl')

    #<meta content="miércoles, 16 de septiembre de 2015 3:30" itemprop="datePublished"
    scrapeddate = scrapertools.find_single_match(data,'<meta content="([^"]+)" itemprop="datePublished')

    item.aired_date = scrapertools.parse_date(scrapeddate)

    item.geolocked = "0"

    media_item = play(item)
    try:
        item.media_url = media_item[0].url.replace("\\","/")
    except:
        import traceback
        print traceback.format_exc()
        item.media_url = ""

    return item

def play(item):
    logger.info("tvalacarta.channels.laredcl play")

    from servers import servertools
    return servertools.find_video_items(item)

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    
    # Mainlist es la lista de programas
    programas_items = mainlist(Item())
    if len(programas_items)==0:
        print "No encuentra los programas"
        return False

    episodios_items = videos(programas_items[0])
    if len(episodios_items)==0:
        print "El programa '"+programas_items[0].title+"' no tiene episodios"
        return False

    return True
