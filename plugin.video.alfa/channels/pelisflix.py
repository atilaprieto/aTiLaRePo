# -*- coding: utf-8 -*-
# -*- Channel pelisflix -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-


import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

from channelselector import get_thumb
from channels import autoplay
from channels import filtertools
from core import httptools
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item
from lib import jsunpack
from platformcode import config, logger


IDIOMAS = {'Latino': 'Latino'}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['fembed', 'streamtape', 'gounlimited', 'directo']


__channel__='pelisflix'

host = "https://pelisflix.io"

try:
    __modo_grafico__ = config.get_setting('modo_grafico', __channel__)
except:
    __modo_grafico__ = True


def mainlist(item):
    logger.info()
    autoplay.init(item.channel, list_servers, list_quality)
    itemlist = []
    itemlist.append(Item(channel = item.channel, title = "Novedades", action = "peliculas", url = host + "/ver-peliculas-online-gratis/page/", page=1, thumbnail = get_thumb("newest", auto = True)))
    itemlist.append(Item(channel = item.channel, title = "Por género", action = "generos", url = host, extra = "Genero", thumbnail = get_thumb("genres", auto = True) ))
    itemlist.append(Item(channel = item.channel, title = ""))
    itemlist.append(Item(channel = item.channel, title = "Buscar", action = "search", url = host + "/?s=", thumbnail = get_thumb("search", auto = True)))
    autoplay.show_option(item.channel, itemlist)
    return itemlist

def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    try:
        if categoria in ['peliculas','latino']:
            item.url = host + "/ver-peliculas-online-gratis/"
        elif categoria == 'infantiles':
            item.url = host + '/genero/animacion/'
        elif categoria == 'terror':
            item.url = host + '/genero/terror/'
        itemlist = peliculas(item)
        if "Pagina" in itemlist[-1].title:
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto
    item.extra = "busca"
    item.page = 1
    if texto != '':
        return peliculas(item)
    else:
        return []


def generos(item):
    logger.info()
    itemlist = []
    totales = 0
    data = httptools.downloadpage(item.url).data
    patron = '(?s)neros</div><ul>(.*?)</li></ul></div></aside>'
    bloque = scrapertools.find_single_match(data, patron)
    patron  = 'href="([^"]+)'
    patron += '">([^<]+).*?'
    patron += '>([^<]+)'
    matches = scrapertools.find_multiple_matches(bloque, patron)
    for url, titulo, cantidad in matches:
        if not url.startswith("http"): url = host + url
        itemlist.append(Item(channel = item.channel,
                             action = "peliculas",
                             title = titulo + " (%s)" %cantidad,
                             url = url + "page/",
                             page = 1,
                             ))
        totales += int(cantidad)
    itemlist.append(Item(channel = item.channel,
                         action = "",
                         title = "Peliculas totales: %s" %totales,
                         url = url + "page/",
                         page = 1,
                         ))
    return itemlist


def peliculas(item):
    logger.info()
    itemlist = []
    if item.extra != "busca":
        data = httptools.downloadpage(item.url + str(item.page)).data
    else:
        data = httptools.downloadpage(item.url).data
    patron  = '<article class="TPost B">.*?'
    patron += 'a href="([^"]+).*?'
    patron += 'data-src="([^"]+).*?'
    patron += 'class="Qlty Yr">([^<]+).*?'
    patron += 'class="Title">([^<]+).*?'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedthumb, scrapedyear, scrapedtitle in matches:
        idioma = "Latino"
        if not scrapedthumb.startswith("http"): scrapedthumb = "https:" + scrapedthumb
        itemlist.append(Item(channel = item.channel,
                                   action = "findvideos",
                                   title = scrapedtitle,
                                   contentTitle = scrapedtitle,
                                   thumbnail = scrapedthumb,
                                   url = scrapedurl,
                                   infoLabels = {"year" :scrapedyear},
                                   language = idioma
                                   ))
    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    if item.extra != "busca":
        item.page += 1
        itemlist.append(Item(channel = item.channel, action = "peliculas", title = "Pagina: %s" %item.page , url = item.url, page = item.page))
    return itemlist


def findvideos(item):
    itemlist = []    
    data = httptools.downloadpage(item.url).data
    matches = scrapertools.find_multiple_matches(data, 'data-key="([^"]+).*?language">([^<]+)' )
    trid = scrapertools.find_single_match(data, 'trid=(\w+)' )
    for id, language in matches:
        data = httptools.downloadpage(host + "/?trembed=%s&trid=%s&trtype=1" %(id, trid)).data
        url = scrapertools.find_single_match(data, 'src="([^"]+)')
        if not url.startswith("http"): url = "https:" + url
        if "pelis28.nu" in url:
            url = httptools.downloadpage(url).data
            url = scrapertools.find_single_match(url, "location.href='([^']+)")
            url = httptools.downloadpage(url).data
            pack = scrapertools.find_single_match(url, "p,a,c,k,e,d.*?</script>")
            unpack = jsunpack.unpack(pack)
            url = scrapertools.find_single_match(unpack, 'file":"([^"]+)')
            url += "|verifypeer=false"
        if "pelis.vip" in url:
            url = scrapertools.find_single_match(url, "v/([A-z0-9_-]+)")
            data = httptools.downloadpage("https://pelis.vip/api/source/%s" %url, post={"r":"", "d":"pelis.vip"}).json
            for datos in data["data"]:
                itemlist.append(Item(
                                    channel=item.channel,
                                    contentTitle=item.contentTitle,
                                    contentThumbnail=item.thumbnail,
                                    infoLabels=item.infoLabels,
                                    language=language,
                                    title=language + ' (%s) ' + datos["label"], action="play",
                                    url=datos["file"]
                                    ))
                
        else:
            itemlist.append(Item(
                                 channel=item.channel,
                                 contentTitle=item.contentTitle,
                                 contentThumbnail=item.thumbnail,
                                 infoLabels=item.infoLabels,
                                 language=language,
                                 title=language + ' (%s)', action="play",
                                 url=url
                                ))

    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())

    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    if itemlist and item.contentChannel != "videolibrary":
        itemlist.append(Item(channel=item.channel))
        itemlist.append(item.clone(channel="trailertools", title="Buscar Tráiler", action="buscartrailer", context="",
                                   text_color="magenta"))

        # Opción "Añadir esta película a la biblioteca de KODI"
        if config.get_videolibrary_support():
            itemlist.append(Item(channel=item.channel, title="Añadir a la videoteca", text_color="green",
                                 action="add_pelicula_to_library", url=item.url, thumbnail = item.thumbnail,
                                 contentTitle = item.contentTitle
                                 ))
    return itemlist


def play(item):
    item.thumbnail = item.contentThumbnail
    return [item]
