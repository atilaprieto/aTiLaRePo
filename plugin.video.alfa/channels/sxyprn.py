# -*- coding: utf-8 -*-
#------------------------------------------------------------
import urlparse,re
from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools

host = 'https://www.sxyprn.com'


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/blog/all/0.html?fl=all&sm=latest"))
    itemlist.append( Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "/popular/top-viewed.html"))
    itemlist.append( Item(channel=item.channel, title="Mejor valorada" , action="lista", url=host + "/popular/top-rated.html"))
    itemlist.append( Item(channel=item.channel, title="Sitios" , action="categorias", url=host))
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = host + "/%s.html" % texto
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
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    if "Sitios" in item.title:
        patron = "<a href='([^']+)' target='_blank'><div class='top_sub_el top_sub_el_sc'>.*?"
        patron += "<span class='top_sub_el_key_sc'>([^<]+)</span>"
        patron += "<span class='top_sub_el_count'>(\d+)</span>"
    else:
        patron = "<a class='tdn' href='([^']+)'.*?"
        patron += "<span class='htag_el_tag'>([^<]+)</span>"
        patron += "<span class='htag_el_count'>(\d+) videos</span>"
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,cantidad in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedurl = urlparse.urljoin(item.url,scrapedurl)
        title = scrapedtitle + " (" + cantidad + ")"
        itemlist.append( Item(channel=item.channel, action="lista", title=title, url=scrapedurl,
                              thumbnail=scrapedthumbnail , plot=scrapedplot) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = "<img class=.*?"
    patron += " src='([^']+)'.*?"
    patron += "post_time' href='([^']+)' title='([^#]+)"
    matches = re.compile(patron,re.DOTALL).findall(data)
    for thumbnail,scrapedurl,scrapedtitle in matches:
        title = scrapedtitle
        if title.startswith("http"):
            scrapedtitle = scrapertools.find_single_match(title, '".*?html([^"]+)"')
        if scrapedtitle =="":
            title = title
        else:
            title = scrapedtitle
        
        if not thumbnail.startswith("https"):
            thumbnail = "https:%s" % thumbnail
        scrapedurl = urlparse.urljoin(item.url,scrapedurl)
        plot = ""
        itemlist.append( Item(channel=item.channel, action="findvideos", title=title, url=scrapedurl,
                              thumbnail=thumbnail, fanart=thumbnail, plot=plot, contentTitle = title))
    next_page = scrapertools.find_single_match(data, "<div class='ctrl_el ctrl_sel'>.*?<a href='([^']+)'")
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append( Item(channel=item.channel, action="lista", title="Página Siguiente >>", text_color="blue", 
                              url=next_page) )
    return itemlist

 # data-vnfo='{"5ebe598bd68c4":"\/cdn\/c10\/xg108c8wzb8m4kzq1q7429zv151o3\/D4ApFJcEQuP2rcd6_AcNTQ\/1589571812\/o5sb9dy8z0abue865dm1r480pdk\/u58edbpe6589m8cb5d16i8scy4s.vid"}'></span>
				# </div>	

def findvideos(item):
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|amp;|\s{2}|&nbsp;", "", data)
    data1 = scrapertools.find_single_match(data, "<div class='main_content'>(.*?)<div class='post_control_time'>")
    logger.debug(data1)
    if "title='>External Link!<'" in data:
        url = scrapertools.find_single_match(data1, "<a href='([^']+)' target='_blank' rel='nofollow' title='>External Link!<'")
        itemlist.append(item.clone(action="play", title= "%s", contentTitle= item.title, url=url))
    url = scrapertools.find_single_match(data, 'data-vnfo=.*?":"([^"]+)"')
    url = url.replace("\/", "/").replace("/cdn/", "/cdn8/")
    url = urlparse.urljoin(item.url,url)
    if url:
        itemlist.append(item.clone(action="play", title= "%s", contentTitle= item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist

