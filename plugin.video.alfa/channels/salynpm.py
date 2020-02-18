# -*- coding: utf-8 -*-
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys
from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools, tmdb

host = 'https://www.salynpm.com'


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append( Item(channel=item.channel, title="Películas" , action="lista", url=host + "/search/label/Pel%C3%ADcula?&max-results=24"))
    # itemlist.append( Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "/?display=tube&filtre=views"))
    # itemlist.append( Item(channel=item.channel, title="Mejor valorada" , action="lista", url=host + "/?display=tube&filtre=rate"))

    itemlist.append( Item(channel=item.channel, title="Géneros" , action="generos", url=host + "/p/categorias.html"))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = host + "/search?q=%s" % texto
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def generos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    data = scrapertools.find_single_match(data, 'Películas</div>(.*?)</div>')
    patron = '<a href="([^"]+)".*?</i>(.*?)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle in matches:
        scrapedplot = ""
        title = scrapedtitle
        scrapedthumbnail =  ""
        itemlist.append( Item(channel=item.channel, action="lista", title=title, url=scrapedurl,
                              thumbnail=scrapedthumbnail , plot=scrapedplot) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    patron = '<div class=\'firstag__content\'>(.*?)</header>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for match in matches:
        url = scrapertools.find_single_match(match,'flex-none\' href=\'([^\']+)\'')
        scrapedtitle = scrapertools.find_single_match(match,'>([^<]+)</a></h2>')
        thumbnail = scrapertools.find_single_match(match,'src=\'([^\']+)\'')
        quality = scrapertools.find_single_match(match,'p\'>([^<]+)</a>')
        title = scrapedtitle
        if quality:
            title = scrapedtitle + " [COLOR red]" + quality + "[/COLOR]"
        scrapedyear = "-"
        plot = ""
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, url=url,
                              thumbnail=thumbnail, fanart=thumbnail, plot=plot, contentTitle = scrapedtitle,
                              quality=quality, infoLabels={'year':scrapedyear}))

    tmdb.set_infoLabels(itemlist, True)

    current_page = scrapertools.find_single_match(item.url, "PageNo=(\d+)")
    base_next_page = scrapertools.find_single_match(data, "<a class='btn btn-kuro' href='([^']+)'>Antiguos<")

    if not current_page:
        next_page = base_next_page.replace("by-date=false", "PageNo=2")
    else:
        base_next_page = base_next_page.replace("&start=24", "")
        next_ = str(int(current_page) + 1)
        next_page = base_next_page.replace("PageNo=%s" % current_page, "PageNo=%s" % next_)

    itemlist.append(Item(channel=item.channel, action="lista", title="Página Siguiente >>", text_color="blue",
                          url=next_page))
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)

    idiomas = scrapertools.find_single_match(data,'Descarga.*?<div class="sinopsis">(.*?)<')
    audios = []
    if "Latino" in idiomas: audios.append('LAT')
    if "Ingles" in idiomas: audios.append('ENG')
    if "Japones" in idiomas: audios.append('JAP')
    if "Subtitulo" in idiomas: audios.append('SUB')
    
    if not config.get_setting('unify'):
        title = '%s (%s)' % (item.quality, " / ".join(audios))
    else:
        title = ""
    
    numero = scrapertools.find_multiple_matches(data,'data-tab="tab\d+">(.*?)</li>')
    numero = len(numero)
    if not numero:
        numero = 1
    n = 1
    patron = '<video class="js-player".*?<source src="([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url in matches:
        url= url.replace("amp;", "")
        if n <= numero:
            itemlist.append(item.clone(action="play", title = "%s " + title, language=audios, url=url ))
            n += 1
    
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    descargas = scrapertools.find_single_match(data,'<a class="button red" href="([^"]+)"')
    itemlist += servertools.find_video_items(item.clone(url = descargas, contentTitle = item.title, language=audios))

    return itemlist

