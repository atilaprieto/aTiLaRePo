# -*- coding: utf-8 -*-
# -*- Channel MasPeliculas -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import re
from bs4 import BeautifulSoup
from channelselector import get_thumb
from core import httptools
from core import scrapertools
import base64
import string
from core import servertools
from core.item import Item
from platformcode import config, logger
from channels import filtertools, autoplay
from core import tmdb

host = "https://maspeliculas.net/"

IDIOMAS = {'castellano': 'CAST', 'latino': 'LAT', 'sub': 'VOSE'}
list_language = IDIOMAS.values()
list_quality = []
list_servers = ['openload',  'rapidvideo', 'clipwatching', 'verystream', 'okru']

def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    itemlist.append(
        Item(channel=item.channel,
             title="Todas",
             action="list_all",
             url=host,
             thumbnail=get_thumb('all', auto=True),
             first=0))

    itemlist.append(
        Item(channel=item.channel,
             title="Ultimas",
             action="list_all",
             url="%s%s" % (host, "peliculas-novedades"),
             thumbnail=get_thumb('last', auto=True),
             first=0))

    itemlist.append(
        Item(channel=item.channel,
             title="Estrenos",
             action="list_all",
             url="%s%s" % (host, "peliculas-de-estreno"),
             thumbnail=get_thumb('premieres', auto=True),
             first=0))

    itemlist.append(
        Item(channel=item.channel,
             title="Audio",
             action="sub_menu",
             thumbnail=get_thumb('audio', auto=True),
             first=0))

    itemlist.append(
        Item(channel=item.channel,
             title="Buscar",
             action="search",
             thumbnail=get_thumb('search', auto=True),
             url='%s%s' % (host, "?s="),
             first=0
             ))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def sub_menu(item):
    logger.info()

    itemlist = list()

    itemlist.append(
        Item(channel=item.channel,
             title="Castellano",
             action="list_all",
             url="%s%s" % (host, "category/castellano"),
             thumbnail=get_thumb('cast', auto=True),
             first=0))

    itemlist.append(
        Item(channel=item.channel,
             title="Latino",
             action="list_all",
             url="%s%s" % (host, "category/latino"),
             thumbnail=get_thumb('lat', auto=True),
             first=0))

    itemlist.append(
        Item(channel=item.channel,
             title="VOSE",
             action="list_all",
             url="%s%s" % (host, "category/VOSE"),
             thumbnail=get_thumb('vose', auto=True),
             first=0))

    return itemlist

def list_all(item):
    logger.info

    itemlist = list()
    next = False
    data = httptools.downloadpage(item.url).data
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")

    matches = soup.find_all("div", class_="post")

    first = item.first
    last = first + 20
    if last >= len(matches):
        last = len(matches)
        next = True

    for elem in matches[first:last]:

        title = ""
        url = elem.a["href"]
        thumb = elem.img["src"]

        langs = elem.find("div", "tituloidioma")
        language = languages_from_flags(langs, "png")

        full_title = elem.find("div", class_="title").text.split('(')
        cleantitle = full_title[0]

        if len(full_title)>1:
            year = re.sub('\)', '', full_title[1])
        else:
            year = '-'
        if not config.get_setting('unify'):
            title = '%s [%s] %s' % (cleantitle, year, language)

        itemlist.append(Item(channel=item.channel, title='%s' %  title, url=url, action='findvideos',
                             contentTitle=cleantitle, thumbnail=thumb, language=language,
                             infoLabels={'year': year}))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    # Pagination

    if not next:
        url_next_page = item.url
        first = last
    else:
        try:
            current = soup.find("span", class_="current").text
        except:
            return itemlist

        url_next_page = '%spage/%s' % (host, str(int(current)+1))
        first = 0

    if url_next_page and len(matches) > 21:
        itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=url_next_page, action='list_all',
                             first=first))
    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()

    data = httptools.downloadpage(item.url).data
    data = scrapertools.unescape(data)

    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    lang = soup.find_all("b")
    lang_list = get_langs(lang)
    lang_count = 0

    for tab_soup in soup.find_all("div", class_="contenedor_tab"):

        lang = lang_list[lang_count]

        for elem in tab_soup.find_all("iframe"):

            title = ""

            enc_url = scrapertools.find_single_match(elem["data-data"], '([^\+]+)\+(.+)?')
            s = base64.b64decode(enc_url[0])
            i = enc_url[1]
            hidden_url = "https://encriptando.com" + s + i
            hidden_data = httptools.downloadpage(hidden_url, follow_redirects=False, headers={'Referer':host}).data
            var, val = scrapertools.find_single_match(hidden_data.replace("'", '"'), 'var (k|s)="([^"]+)";')
            url = decrypt(var, val)
            if var == "k":
                url += "|%s" % item.url

            if not config.get_setting('unify'):
                title = ' [%s]' % lang

            itemlist.append(Item(channel=item.channel, title='%s'+ title, url=url, action='play', language=lang,
                            infoLabels=item.infoLabels))

        lang_count += 1
    itemlist = servertools.get_servers_itemlist(itemlist, lambda x: x.title % x.server.capitalize())

    # Requerido para FilterTools

    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos':
        itemlist.append(Item(channel=item.channel, title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
                             url=item.url, action="add_pelicula_to_library", extra="findvideos",
                             contentTitle=item.contentTitle))

    return itemlist


def get_langs(lang):
    lang_list = list()
    for l in lang:

        if 'CALIDAD' not in l.text:
            lang.remove(l)
        else:
            if 'castellano' in l.text.lower():
                lang_list.append('CAST')
            elif 'latino' in l.text.lower():
                lang_list.append('LAT')
            else:
                lang_list.append('VOSE')

    return lang_list


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto
    item.first = 0
    if texto != '':
        return list_all(item)
    else:
        return []

def decrypt(var, val):

    d = ""

    if var == 'k':
        a = base64.b64decode(val[1:])

        c = 1
        while c < len(a):
            d += chr(int(a[c:c + 2], 16))
            c += 2

    elif var == 's':
        a = base64.b64decode(val[2:])
        for c in a:
            if c not in string.ascii_letters:
                d += c
            else:
                n = (ord(c)) / 97
                x = 26 if (ord(c.lower()) - 83) % 26 == 0 else (ord(c.lower()) - 83) % 26
                d += chr(x + 96) if n != 0 else chr(x+64)
    return d


def languages_from_flags(lang_data, ext):
    logger.info()
    language = []

    lang_list = lang_data.find_all("img")

    for lang in lang_list:
        lang = scrapertools.find_single_match(lang["src"], "(\w+).%s" % ext)

        language.append(IDIOMAS.get(lang, "VOSE"))
    return language
