# -*- coding: utf-8 -*-
# -*- Channel Destotal -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

from builtins import map
from builtins import range

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    #from future import standard_library
    #standard_library.install_aliases()
    import urllib.parse as urllib                               # Es muy lento en PY2.  En PY3 es nativo
else:
    import urllib                                               # Usamos el nativo de PY2 que es más rápido

import re
from core import tmdb
from core import httptools
from core.item import Item
from core import servertools
from core import scrapertools
from bs4 import BeautifulSoup
from channelselector import get_thumb
from platformcode import config, logger
from channels import filtertools, autoplay

IDIOMAS = {'latino': 'Latino', 'castellano': 'Castellano', 'portugues': 'Portugues'}
list_language = list(IDIOMAS.values())
list_quality = ['1080p']
list_servers = ['gounlimited',
                'mega',
                'vidcloud',
                'torrent'
                ]

host = 'https://www.cinecalidad.is'

thumbmx = 'http://flags.fmcdn.net/data/flags/normal/mx.png'
thumbes = 'http://flags.fmcdn.net/data/flags/normal/es.png'
thumbbr = 'http://flags.fmcdn.net/data/flags/normal/br.png'

current_lang = ''

site_list = ['', 'cinecalidad.is/', 'cinecalidad.is/espana/', 'cinemaqualidade.is/']
site = config.get_setting('filter_site', channel='cinecalidad')
site_lang = 'https://www.%s' % site_list[site]

def mainlist(item):
    logger.info()

    itemlist = list()
    idioma2 = "destacadas"

    if site > 0:
        item.action = 'submenu'
        item.host = site_lang
        return submenu(item)

    autoplay.init(item.channel, list_servers, list_quality)
    itemlist = []

    itemlist.append(Item(channel=item.channel,
                         title="CineCalidad Latino",
                         action="submenu",
                         host="https://www.cinecalidad.is/",
                         thumbnail=thumbmx))

    itemlist.append(Item(channel=item.channel,
                         title="CineCalidad Castellano",
                         action="submenu",
                         host="https://www.cinecalidad.is/espana/",
                         thumbnail=thumbes))

    itemlist.append(Item(channel=item.channel,
                         title="CineCalidad Portugues",
                         action="submenu",
                         host="https://www.cinemaqualidade.is/",
                         thumbnail=thumbbr))

    itemlist.append(Item(channel=item.channel,
                         title="Configurar Canal...",
                         text_color="turquoise",
                         action="settingCanal",
                         thumbnail=get_thumb('setting_0.png'),
                         url='',
                         fanart=get_thumb('setting_0.png')
                         ))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def submenu(item):
    idioma = 'peliculas'
    idioma2 = "destacada"
    host = item.host
    if item.host == "https://www.cinemaqualidade.is/":
        idioma = "filmes"
        idioma2 = "destacado"
    logger.info()
    itemlist = []

    itemlist.append(Item(channel=item.channel,
                         title=idioma.capitalize(),
                         action="list_all",
                         url=host,
                         thumbnail=get_thumb('movies', auto=True),
                         ))
    itemlist.append(Item(channel=item.channel,
                         title="Destacadas",
                         action="list_all",
                         url=host + "/genero-" + idioma + "/" + idioma2 + "/",
                         thumbnail=get_thumb('hot', auto=True),
                         ))
    itemlist.append(Item(channel=item.channel,
                         title="Generos",
                         action="genres",
                         url=host,
                         thumbnail=get_thumb('genres', auto=True),
                         ))
    itemlist.append(Item(channel=item.channel,
                         title="Por Año",
                         action="by_year",
                         url=host + idioma + "-por-ano",
                         thumbnail=get_thumb('year', auto=True),
                         ))
    itemlist.append(Item(channel=item.channel,
                         title="Buscar...",
                         action="search",
                         thumbnail=get_thumb('search', auto=True),
                         url=host + '/?s=',
                         host=item.host,
                         ))
    if site > 0:
        autoplay.init(item.channel, list_servers, list_quality)

        itemlist.append(Item(channel=item.channel,
                             title="Configurar Canal...",
                             text_color="turquoise",
                             action="settingCanal",
                             thumbnail=get_thumb('setting_0.png'),
                             url='',
                             fanart=get_thumb('setting_0.png')
                             ))

        autoplay.show_option(item.channel, itemlist)

    return itemlist


def create_soup(url, referer=None, unescape=False):
    logger.info()

    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}).data
    else:
        data = httptools.downloadpage(url).data

    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")

    return soup

def list_all(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url, unescape=True)
    for elem in soup.find_all("div", class_="home_post_cont"):
        url = elem.a["href"]
        try:
            title, year = elem.img["title"].split(' (')
            year = re.sub(r"\)","", year)
        except:
            continue
        thumb = re.sub(r'(-\d+x\d+.jpg)', '.jpg', elem.img["src"])
        if elem.p: 
            plot = elem.p.text
        else:
            plot = ''
        itemlist.append(Item(channel=item.channel, title=title, url=url, thumbnail=thumb, action="findvideos",
                             plot=plot, contentTitle=title, infoLabels={'year': year}))
    tmdb.set_infoLabels_itemlist(itemlist, True)

    ## Pagination ##

    try:
        next_page = soup.find("a", class_="nextpostslink")["href"]
        itemlist.append(Item(channel=item.channel,  action="list_all",  title="Página siguiente >>",
                             url=next_page, language=item.language ))
    except:
        pass

    return itemlist

def by_year(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url, unescape=True).find("div", class_="page_single_left")

    for elem in soup.find_all('a'):
        url = elem["href"]
        title = elem.text
        itemlist.append(Item(channel=item.channel, title=title, url=url, action="list_all"))

    return itemlist

def genres(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url, unescape=True).find("ul")
    for elem in soup.find_all("li", class_=re.compile("menu-item-object-category")):
        url = elem.a["href"]
        title = elem.a.text
        if not url.startswith('http'):
            url = host +url
        
        itemlist.append(Item(channel=item.channel, title=title, url=url, action="list_all"))

    return itemlist


def settingCanal(item):
    from platformcode import platformtools
    platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    return


def dec(item, dec_value):
    link = []
    val = item.split(' ')
    link = list(map(int, val))
    for i in range(len(link)):
        link[i] = link[i] - int(dec_value)
        real = ''.join(map(chr, link))
    return (real)


def findvideos(item):

    logger.info()
    itemlist = []
    duplicados = []

    if 'cinemaqualidade' in item.url:
        lang = 'portugues'
    elif 'espana' in item.url:
        lang = 'castellano'
    elif 'cinecalidad' in item.url:
        lang = 'latino'
    
    data = httptools.downloadpage(item.url).data
    patron = 'target=_blank.*? service=.*? data="(.*?)"><li>(.*?)<\/li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    patronk = '<a href="(/vip/v.php\?i=.*?")'
    matchesk = re.compile(patronk, re.DOTALL).findall(data)

    server_url = {'yourupload': 'https://www.yourupload.com/embed/%s',
                  'trailer': 'https://www.youtube.com/embed/%s',
                  'bittorrent': '',
                  'mega': 'https://mega.nz/file/%s',
                  'fembed': 'https://www.fembed.com/v/%s',
                  'gounlimited': 'https://gounlimited.to/embed-%s.html',
                  'clipwatching': 'https://clipwatching.com/embed-%s.html',
                  'vidcloud': 'https://vidcloud.co/embed/%s',
                  'jetload': 'https://jetload.net/e/%s'}
    
    dec_value = scrapertools.find_single_match(data, 'String\.fromCharCode\(parseInt\(str\[i\]\)-(\d+)\)')
    torrent_link = scrapertools.find_single_match(data, '<a href=".*?/protect/v\.php\?i=([^"]+)"')
    subs = scrapertools.find_single_match(data, '<a id=subsforlink href=(.*?) ')

    for scrapedurl in matchesk:
        
        base_url = host + scrapedurl
        
        headers={'Cookie': 'codigovip=100734121;'}
        protect = httptools.downloadpage(base_url, headers=headers).data
        
        url = scrapertools.find_single_match(protect, 'font-size:1.05em"><a href="([^"]+)')
        server = servertools.get_server_from_url(url)

        title = '(%s)' % server.capitalize()
        quality = '4K'
        language = IDIOMAS[lang]
        if url:
            new_item = Item(channel=item.channel,
                            action='play',
                            title=title,
                            contentTitle=item.contentTitle,
                            url=url,
                            language=language,
                            thumbnail=item.thumbnail,
                            quality=quality,
                            server=server
                            )
            itemlist.append(new_item)
    
    if torrent_link != '':
        base_url = '%s/protect/v.php' % host
        post = {'i': torrent_link, 'title': item.title}
        post = urllib.urlencode(post)
        headers = {'Referer': item.url}
        protect = httptools.downloadpage(base_url + '?' + post, headers=headers).data
        url = scrapertools.find_single_match(protect, 'value="(magnet.*?)"')
        server = 'torrent'

        title = item.contentTitle + ' (%s)' % server
        quality = '1080p'
        language = IDIOMAS[lang]

        new_item = Item(channel=item.channel,
                        action='play',
                        title=title,
                        contentTitle=item.contentTitle,
                        url=url,
                        language=language,
                        thumbnail=item.thumbnail,
                        quality=quality,
                        server=server
                        )
        itemlist.append(new_item)

    for video_cod, server_id in matches:
        thumbnail = item.thumbnail
        server = server_id.lower()
        if server in server_url and server not in duplicados:
            video_id = dec(video_cod, dec_value)

            url = server_url.get(server, '')
            
            title = '(%s)' % server.capitalize()
            quality = '1080p'
            language = IDIOMAS[lang]
            if url:
                url = url % video_id
                new_item = Item(channel=item.channel,
                                action='play',
                                title=server.capitalize(),
                                contentTitle=item.contentTitle,
                                url=url,
                                language=language,
                                thumbnail=thumbnail,
                                quality=quality,
                                server=server,
                                subtitle=subs
                                )
                itemlist.append(new_item)
                duplicados.append(server)


    # Requerido para FilterTools

    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    # itemlist.append(trailer_item)
    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos':
        itemlist.append(
            Item(channel=item.channel,
                 title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
                 url=item.url,
                 action="add_pelicula_to_library",
                 extra="findvideos",
                 contentTitle=item.contentTitle,
                 ))

    return itemlist


def get_urls(item, link):
    logger.info()
    url = 'http://www.cinecalidad.is/ccstream/ccstream.php'
    headers = dict()
    headers["Referer"] = item.url
    post = 'link=%s' % link

    dict_data = httptools.downloadpage(url, post=post, headers=headers).json
    return dict_data['link']


def play(item):
    logger.info()
    itemlist = []
    if 'juicyapi' not in item.url:
        itemlist = servertools.find_video_items(data=item.url)

        for videoitem in itemlist:
            videoitem.title = item.contentTitle
            videoitem.contentTitle = item.contentTitle
            videoitem.thumbnail = item.thumbnail
            videoitem.channel = item.channel
            videoitem.subtitle = item.subtitle
    else:
        itemlist.append(item)

    return itemlist


def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    try:
        if categoria in ['peliculas', 'latino']:
            item.url = 'http://www.cinecalidad.is'
        elif categoria == 'infantiles':
            item.url = 'http://www.cinecalidad.is/genero-peliculas/infantil/'
        elif categoria == 'terror':
            item.url = 'http://www.cinecalidad.is/genero-peliculas/terror/'
        elif categoria == 'castellano':
            item.url = 'http://www.cinecalidad.is/espana/'
        itemlist = list_all(item)
        if itemlist[-1].title == 'Página siguiente >>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def search(item, texto):
    logger.info()
    itemlist = []

    texto = texto.replace(" ", "-")

    if item.host != '':
        host_list = [item.host]
    elif site:
        item.gb_search = True
        host_list = [site_lang]
    else:
        item.gb_search = True
        host_list = ['http://www.cinecalidad.is/espana/', 'http://www.cinecalidad.is/']

    for host_name in host_list:
        item.url = host_name + '?s=' + texto
        if texto != '':
            itemlist.extend(list_all(item))

    return itemlist