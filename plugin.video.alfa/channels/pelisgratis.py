# -*- coding: utf-8 -*-

import re
import urllib
import base64

from core import httptools
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item
from platformcode import config, logger
from channelselector import get_thumb


thumbletras = {'#': 'https://s32.postimg.cc/drojt686d/image.png',
               'a': 'https://s32.postimg.cc/llp5ekfz9/image.png',
               'b': 'https://s32.postimg.cc/y1qgm1yp1/image.png',
               'c': 'https://s32.postimg.cc/vlon87gmd/image.png',
               'd': 'https://s32.postimg.cc/3zlvnix9h/image.png',
               'e': 'https://s32.postimg.cc/bgv32qmsl/image.png',
               'f': 'https://s32.postimg.cc/y6u7vq605/image.png',
               'g': 'https://s32.postimg.cc/9237ib6jp/image.png',
               'h': 'https://s32.postimg.cc/812yt6pk5/image.png',
               'i': 'https://s32.postimg.cc/6nbbxvqat/image.png',
               'j': 'https://s32.postimg.cc/axpztgvdx/image.png',
               'k': 'https://s32.postimg.cc/976yrzdut/image.png',
               'l': 'https://s32.postimg.cc/fmal2e9yd/image.png',
               'm': 'https://s32.postimg.cc/m19lz2go5/image.png',
               'n': 'https://s32.postimg.cc/b2ycgvs2t/image.png',
               'o': 'https://s32.postimg.cc/c6igsucpx/image.png',
               'p': 'https://s32.postimg.cc/jnro82291/image.png',
               'q': 'https://s32.postimg.cc/ve5lpfv1h/image.png',
               'r': 'https://s32.postimg.cc/nmovqvqw5/image.png',
               's': 'https://s32.postimg.cc/zd2t89jol/image.png',
               't': 'https://s32.postimg.cc/wk9lo8jc5/image.png',
               'u': 'https://s32.postimg.cc/w8s5bh2w5/image.png',
               'v': 'https://s32.postimg.cc/e7dlrey91/image.png',
               'w': 'https://s32.postimg.cc/fnp49k15x/image.png',
               'x': 'https://s32.postimg.cc/dkep1w1d1/image.png',
               'y': 'https://s32.postimg.cc/um7j3zg85/image.png',
               'z': 'https://s32.postimg.cc/jb4vfm9d1/image.png'
               }

audio_color = {'LAT': '[COLOR limegreen][LAT][/COLOR]',
               'CAST': '[COLOR golden][CAST][/COLOR]',
               'VOSE': '[COLOR grey][VOSE][/COLOR]'}

IDIOMAS = {'latino': 'LAT', 'espanol': 'CAST', 'castellano': 'CAST',
           'subtitulado': 'VOSE', 'subtitulo': 'VOSE'}

list_language = IDIOMAS.values()

list_quality = ['BRRip', 'HDRip', 'DVD-R', 'HDTv-rip', 'BR-Screener',
                'WEB-S', 'TS-HQ', 'TS-Screener']

list_servers = ['rapidvideo', 'verystream', 'streamplay']

host = 'http://pelisgratis.live/'


def mainlist(item):
    logger.info()

    itemlist = []

    itemlist.append(item.clone(title="Estrenos",
                               action="lista",
                               thumbnail=get_thumb('premieres', auto=True),
                               url=host + 'estrenos'
                               ))

    itemlist.append(item.clone(title="Últimas",
                               action="lista",
                               thumbnail=get_thumb('last', auto=True),
                               url=host
                               ))

    itemlist.append(item.clone(title="Generos",
                               action="seccion",
                               url=host,
                               thumbnail=get_thumb('genres', auto=True),
                               extra='generos'
                               ))

    itemlist.append(item.clone(title="Alfabetico",
                               action="seccion",
                               url=host + 'estrenos',
                               thumbnail=get_thumb('alphabet', auto=True),
                               extra='a-z'
                               ))

    '''itemlist.append(item.clone(title="Mas Vistas",
                               action="lista",
                               thumbnail=get_thumb('more watched', auto=True),
                               url=host + 'peliculas-mas-vistas'
                               ))

    itemlist.append(item.clone(title="Mas Votadas",
                               action="lista",
                               thumbnail=get_thumb('more voted', auto=True),
                               url=host + 'peliculas-mas-votadas'
                               ))'''

    itemlist.append(item.clone(title="Buscar...",
                               action="search",
                               url=host + '?s=',
                               thumbnail=get_thumb('search', auto=True)
                               ))

    return itemlist


def get_source(url, referer=None):
    logger.info()
    if referer is None:
        data = httptools.downloadpage(url).data
    else:
        data = httptools.downloadpage(url, headers={'Referer':referer}).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    return data


def lista(item):
    logger.info()
    itemlist = []
    data = get_source(item.url)
    patron = '<article class="item.*?href="([^"]+)" title="([^"]+)">(.*?)<img.*?src="([^"]+)"'

    matches = re.compile(patron, re.DOTALL).findall(data)
    
    for url, scrapedtitle, info_data, scrapedthumbnail in matches:
        
        quality = scrapertools.find_single_match(info_data, 'class="calidad">([^<]+)</div>')
        info_data = scrapertools.find_single_match(info_data, '<div class="audio">(.*?)</div></div>')
        list_langs = re.compile('<div class="([^"]+)"', re.DOTALL).findall(info_data)

        zanga, list_langs = extrae_idiomas(list_langs)

        thumbnail = re.sub('p/w\d+', "p/original", scrapedthumbnail)
        filter_thumb = re.sub('(.*?)/w\d+', "", scrapedthumbnail)
        filter_list = {"poster_path": filter_thumb}
        infoLabels = {'filtro': filter_list.items()}

        year = scrapertools.find_single_match(url, '-(\d{4})')
        if year:
            infoLabels =  {'year': year}
        
        title = scrapedtitle
        stitle = re.sub(' \((.*?)\)$', '', scrapedtitle)
        #excepcion para unify
        title += ' [COLOR grey][%s][/COLOR][COLOR khaki] %s[/COLOR]' % (quality, zanga)

        itemlist.append(item.clone(action='findvideos',
                                   title=title,
                                   url=url,
                                   thumbnail=thumbnail,
                                   contentTitle=stitle,
                                   quality=quality,
                                   language=list_langs,
                                   infoLabels=infoLabels
                                   ))
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)
    
    # Paginacion
    if len(itemlist):
        next_page = scrapertools.find_single_match(data, 'href="([^"]+)" aria-label="Siguiente"')
        if next_page:
            itemlist.append(item.clone(action="lista",
                                       title='Siguiente >>>',
                                       url=next_page,
                                       thumbnail='https://s32.postimg.cc/4zppxf5j9/siguiente.png'
                                       ))
    return itemlist


def seccion(item):
    logger.info()
    itemlist = []
    data = get_source(item.url)
    if item.extra == 'generos':
        patron = 'menu-item-object-category.*?<a href="([^"]+)">([^<]+)</a>'
    elif item.extra == 'a-z':
        patron = '<li><a href="([^"]+)">(\w|#)<\/a><\/li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        url = scrapedurl
        thumbnail = ''
        if item.extra == 'generos':
            title = scrapedtitle
        else:
            title = scrapedtitle
            if title.lower() in thumbletras:
                thumbnail = thumbletras[title.lower()]

        itemlist.append(item.clone(action='lista', title=title, url=url, thumbnail=thumbnail))

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto
    if texto != '':
        return lista(item)


def findvideos(item):
    logger.info()
    itemlist = []
    global new_data
    new_data = []
    data = get_source(item.url)
    
    patron = 'aria-labelledby="([^"]+)">(.*?)</li>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedlang, data in matches:

        if 'trail' in scrapedlang.lower():
            continue
        
        language = IDIOMAS.get(scrapedlang, scrapedlang)
        lang = audio_color.get(language, language)

        patron = '<a id="enlace".*?data-href="([^"]+)">.*?<img src.*?>([^<])'
        matches = scrapertools.find_multiple_matches(data, patron)

        for scrapedurl, info in matches:
            
            scrapedurl += "=="
            urls_page = base64.b64decode(scrapedurl)
            if "repro.live" in urls_page:
                server_repro(urls_page, item.url)
            elif "itatroniks.com" in urls_page:
                server_itatroniks(urls_page)
            else:
                new_data = [urls_page]
            for url in new_data:
                itemlist.append(item.clone(title='[%s] %s',
                                url=url,
                                action='play',
                                language=language,
                                lang=lang
                                ))
            new_data = []
    itemlist = servertools.get_servers_itemlist(itemlist, lambda x: x.title % (x.server.capitalize(), x.lang))
    return itemlist


def server_itatroniks(urls_page):
    logger.info()
    headers = {"Referer":urls_page}
    id = scrapertools.find_single_match(urls_page, 'embed/(\w+)')
    sub_data = httptools.downloadpage(urls_page, headers = headers).data
    matches = scrapertools.find_multiple_matches(sub_data, 'button id="([^"]+)')
    headers1 = ({"X-Requested-With":"XMLHttpRequest"})
    for serv in matches:
        data_json = httptools.downloadpage("https://itatroniks.com/get/%s/%s" %(id, serv), headers=headers1).json
        urls_page = ""
        try:
            if "finished" == data_json["status"]: urls_page = "https://%s/embed/%s" %(data_json["server"], data_json["extid"])
            if "propio" == data_json["status"]: urls_page = "https://%s/e/%s" %(data_json["server"], data_json["extid"])
        except:
            continue
        new_data.append(urls_page)



def server_repro(urls_page, ref):
    logger.info()
    headers = {"Referer":ref}
    sub_data = httptools.downloadpage(urls_page, headers = headers).data
    urls_page1 = scrapertools.find_multiple_matches(sub_data, 'data-embed="([^"]+)"')
    
    for urls_page in urls_page1:
        urls_page += "=="
        urls_page = base64.b64decode(urls_page)
        
        if "repro.live" in urls_page:
            data1 = httptools.downloadpage(urls_page, headers = headers).data
            urls_page1 = scrapertools.find_multiple_matches(data1, 'source src="([^"]+)')
            for urls_page in urls_page1:
                new_data.append(urls_page)
        else:
            new_data.append(urls_page)


def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    # categoria='peliculas'
    try:
        if categoria == 'peliculas':
            item.url = host + 'estrenos'
        elif categoria == 'infantiles':
            item.url = host + 'animacion'
        elif categoria == 'terror':
            item.url = host + 'terror'
        itemlist = lista(item)
        if itemlist[-1].title == 'Siguiente >>>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def extrae_idiomas(list_language):
    logger.info()
    language=[]
    textoidiomas = ''
    
    for i, idioma in enumerate(list_language):
        lang = IDIOMAS.get(idioma, idioma)
        textoidiomas += "[%s] " % lang
        list_language[i] = lang
    
    return textoidiomas, list_language

def play(item):
    if 'video.pelisgratis.' in item.url:
        b_url = scrapertools.find_single_match(item.url, 'tor/(.*?)/')
        b_url = base64.b64decode(b_url+'==')
        try:
            l_url = b_url.split('[#]')
            n = len(l_url) - 1
            item.url = l_url[n]
            item.server='oprem'
        except:
            item.url = ''

    return [item]

