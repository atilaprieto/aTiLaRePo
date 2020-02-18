# -*- coding: utf-8 -*-
#------------------------------------------------------------
import urlparse,re

from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools

host = 'https://tubepornclassic.com'

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/latest-updates/"))
    itemlist.append( Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "/most-popular/"))
    itemlist.append( Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "/top-rated/"))
    itemlist.append( Item(channel=item.channel, title="PornStar" , action="catalogo", url=host + "/models/"))
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="catalogo", url=host + "/categories/"))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = host + "/search/videos/%s/" % texto
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
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    logger.debug(data)
    patron = '<a class="item" href="([^"]+)".*?'
    patron += 'src="([^"]+)"\s+alt="([^"]+)".*?'
    patron += '<div class="videos">([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle, cantidad in matches:
    
        title = "%s (%s)" %(scrapedtitle,cantidad)
        thumbnail = scrapedthumbnail
        url = urlparse.urljoin(item.url,scrapedurl)
        itemlist.append( Item(channel=item.channel, action="lista", title=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail, plot="") )
    next_page = scrapertools.find_single_match(data, '<li class="next">.*?<a href="([^"]+)"')
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append( Item(channel=item.channel, action="catalogo", title="Página Siguiente >>", text_color="blue", 
                              url=next_page) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<div class="item  ">.*?'
    patron += 'href="([^"]+)".*?'
    patron += 'src="([^"]+)".*?'
    patron += 'alt="([^"]+)".*?'
    patron += '<div class="duration">([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,time in matches:
        time = time.strip()
        title = "[COLOR yellow]%s[/COLOR] %s" % (time, scrapedtitle)
        thumbnail = scrapedthumbnail
        url = urlparse.urljoin(item.url,scrapedurl)
        plot = ""
        itemlist.append( Item(channel=item.channel, action="play", title=title, url=url,
                              thumbnail=thumbnail, fanart=thumbnail, plot=plot, contentTitle = title))
    next_page = scrapertools.find_single_match(data, '<li class="next">.*?<a href="([^"]+)"')
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append( Item(channel=item.channel, action="lista", title="Página Siguiente >>", text_color="blue", 
                              url=next_page) )
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

