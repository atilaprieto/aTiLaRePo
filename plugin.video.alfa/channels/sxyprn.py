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
    patron += "<span class='duration_small'.*?'>([^<]+)<.*?"
    patron += "<span class='shd_small'.*?>([^<]+)<.*?"
    patron += "post_time' href='([^']+)' title='([^']+)'"
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedthumbnail,scrapedtime,quality,scrapedurl,scrapedtitle in matches:
        title = "[COLOR yellow]%s[/COLOR] [COLOR red]%s[/COLOR] %s" % (scrapedtime,quality,scrapedtitle)
        thumbnail = "https:" + scrapedthumbnail
        scrapedurl = urlparse.urljoin(item.url,scrapedurl)
        plot = ""
        itemlist.append( Item(channel=item.channel, action="play", title=title, url=scrapedurl,
                              thumbnail=thumbnail, fanart=thumbnail, plot=plot, contentTitle = scrapedtitle))
                              # 
    next_page = scrapertools.find_single_match(data, "<div class='ctrl_el ctrl_sel'>.*?<a href='([^']+)'")
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append( Item(channel=item.channel, action="lista", title="Página Siguiente >>", text_color="blue", 
                              url=next_page) )
    return itemlist
                                                                                                      130
           https://www.sxyprn.com/cdn8/c9/e1y9b3mzc1o101lzg5q2cze1j390h/kK-CN4l73_EeBhkoYNYA2A/1568228307/65xbtac5i3dbd568c4r9z4575at/g5fd37a74djew1zev21dm176g86.vid
data-vnfo='{"5d77de1e2d168":"\/cdn\/c9\/e1y9b3mzc1o101lzg5q2cze1j390h\/kK-CN4l73_EeBhkoYNYA2A\/1568228437\/65xbtac5i3dbd568c4r9z4575at\/g5fd37a74djew1zev21dm176g86.vid
                                                                                                     -114
data-vnfo='{"5d77de1e2d168":"\/cdn\/c9\/m1v963ez51m1u11za5u2xz41e3806\/BQFIcJlTMr0-Z1gVUTxgaQ\/1568228604\/je54bwaz5r3xbn5a864k91487sa\/o5sd17r7xdaea1be32xd41b6b8z.vid
           https://www.sxyprn.com/cdn8/c9/m1v963ez51m1u11za5u2xz41e3806/BQFIcJlTMr0-Z1gVUTxgaQ/1568228490/je54bwaz5r3xbn5a864k91487sa/o5sd17r7xdaea1be32xd41b6b8z.vid
                                                                                                     -137
data-vnfo='{"5d77de1e2d168":"\/cdn\/c9\/5v1n993kzs1n1f1ozc5b20zg1o350\/NCnvDdBfOQmJOivEflNSww\/1568229437\/05pbja75c39br5m8q41974z7haf\/v85edl7b76diej12eb2wd7136v8.vid
           https://www.sxyprn.com/cdn8/c9/5v1n993kzs1n1f1ozc5b20zg1o350/NCnvDdBfOQmJOivEflNSww/1568229300/05pbja75c39br5m8q41974z7haf/v85edl7b76diej12eb2wd7136v8.vid

                                                                                                     -106
data-vnfo='{"5d77de1e2d168":"\/cdn\/c9\/41v9b3nzc1q1615zr5n2szw153905\/9LeO2lux-GrgOaEPfMONcA\/1568230473\/1d52b3aa5s36bt5d8o4a9m427pa\/zh5sdc7k7ndee11qe42sdz1h6j8.vid
           https://www.sxyprn.com/cdn8/c9/41v9b3nzc1q1615zr5n2szw153905/9LeO2lux-GrgOaEPfMONcA/1568230367/1d52b3aa5s36bt5d8o4a9m427pa/zh5sdc7k7ndee11qe42sdz1h6j8.vid

https://c9.trafficdeposit.com/vidi/m1v963ez51m1u11za5u2xz41e3806/BQFIcJlTMr0-Z1gVUTxgaQ/1568228490/5ba53b584947a/5d77de1e2d168.vid
https://c9.trafficdeposit.com/vidi/e1y9b3mzc1o101lzg5q2cze1j390h/kK-CN4l73_EeBhkoYNYA2A/1568228307/5ba53b584947a/5d77de1e2d168.vid
                                    + + +   + + +   + +   + + +
                                    193111152130
                                     + + +   + + +   + +   + + +
https://c9.trafficdeposit.com/vidi/5v1n993kzs1n1f1ozc5b20zg1o350/NCnvDdBfOQmJOivEflNSww/1568229300/5ba53b584947a/5d77de1e2d168.vid

https://c9.trafficdeposit.com/vidi/m1v963ez51m1u11za5u2xz41e3806/NCnvDdBfOQmJOivEflNSww/1568229300/5ba53b584947a/5d77de1e2d168.vid


def play(item):
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|amp;|\s{2}|&nbsp;", "", data)
    url = scrapertools.find_single_match(data, 'data-vnfo=.*?":"([^"]+)"')
    url = url.replace("\/", "/").replace("/cdn/", "/cdn8/")
    url = urlparse.urljoin(item.url,url)
    itemlist = servertools.find_video_items(item.clone(url = url, contentTitle = item.title))
    # itemlist.append( Item(channel=item.channel, action="play",server=directo, title = item.title, url=url))
    return itemlist

