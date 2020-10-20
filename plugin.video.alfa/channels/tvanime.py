# -*- coding: utf-8 -*-
# -*- Channel TVAnime -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urllib                                               # Es muy lento en PY2.  En PY3 es nativo
else:
    import urllib                                                               # Usamos el nativo de PY2 que es más rápido

import re

from core import httptools
from core import scrapertools
from core import servertools
from channelselector import get_thumb
from core import tmdb
from core.item import Item
from platformcode import logger, config
from channels import autoplay
from channels import filtertools
from channels import renumbertools

host = "https://monoschinos.com/"

__comprueba_enlaces__ = config.get_setting('comprueba_enlaces', 'tvanime')
__comprueba_enlaces_num__ = config.get_setting('comprueba_enlaces_num', 'tvanime')

epsxfolder = config.get_setting('epsxfolder', 'tvanime')

IDIOMAS = {'VOSE': 'VOSE', 'Latino':'LAT', 'Castellano':'CAST'}
list_epsxf = {0: None, 1: 25, 2: 50, 3: 100}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['directo', 'openload', 'streamango']

def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = []

    itemlist.append(Item(channel=item.channel, title="Nuevos Episodios",
                         action="new_episodes",
                         thumbnail=get_thumb('new_episodes', auto=True),
                         url=host))

    itemlist.append(Item(channel=item.channel, title="Ultimas",
                               action="list_all",
                               thumbnail=get_thumb('last', auto=True),
                               url=host + 'emision'))

    itemlist.append(Item(channel=item.channel, title="Todas",
                               action="list_all",
                               thumbnail=get_thumb('all', auto=True),
                               url=host + 'animes'))

    itemlist.append(Item(channel=item.channel, title="Anime",
                              action="list_all",
                              thumbnail=get_thumb('anime', auto=True),
                              url=host + 'categoria/anime'))

    itemlist.append(Item(channel=item.channel, title="Películas",
                         action="list_all",
                         thumbnail=get_thumb('movies', auto=True),
                         url=host + 'categoria/pelicula'))

    itemlist.append(Item(channel=item.channel, title="OVAs",
                              action="list_all",
                              thumbnail='',
                              url=host + 'categoria/ova'))

    itemlist.append(Item(channel=item.channel, title="ONAs",
                              action="list_all",
                              thumbnail='',
                              url=host + 'categoria/ona'))

    itemlist.append(Item(channel=item.channel, title="Especiales",
                              action="list_all",
                              thumbnail='',
                              url=host + 'categoria/especial'))

    itemlist.append(Item(channel=item.channel, title="A - Z",
                         action="section",
                         thumbnail=get_thumb('alphabet', auto=True),
                         url=host + 'animes',
                         mode="letra"))

    itemlist.append(Item(channel=item.channel, title="Generos",
                         action="section",
                         thumbnail=get_thumb('genres', auto=True),
                         url=host + 'animes',
                         mode="genero"))

    itemlist.append(Item(channel=item.channel, title="Buscar",
                               action="search",
                               url=host + 'search?q=',
                               thumbnail=get_thumb('search', auto=True),
                               fanart='https://s30.postimg.cc/pei7txpa9/buscar.png'
                               ))

    itemlist.append(Item(channel=item.channel,
                             title="Configurar Canal...",
                             text_color="turquoise",
                             action="settingCanal",
                             thumbnail=get_thumb('setting_0.png'),
                             url='',
                             fanart=get_thumb('setting_0.png')
                             ))

    autoplay.show_option(item.channel, itemlist)
    itemlist = renumbertools.show_option(item.channel, itemlist)

    return itemlist

def settingCanal(item):
    from platformcode import platformtools
    platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    return


def get_source(url):
    logger.info()
    data = httptools.downloadpage(url).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    return data


def list_all(item):
    logger.info()

    itemlist = []

    data = get_source(item.url)
    patron = '<article.*?href="([^"]+)">.*?src="([^"]+)".*?'
    patron +=  '<h3 class="Title">([^<]+)</h3>.*?"fecha">([^<]+)<.*?</i>([^<]+)'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle, year, type in matches:
        type = type.strip().lower()
        url = scrapedurl
        thumbnail = re.sub("image/imagen/160/224/", "assets/img/serie/imagen/", scrapedthumbnail)
        lang, title = clear_title(scrapedtitle)
        stitle = title
        
        if not config.get_setting('unify'):
            stitle += ' [COLOR lightsteelblue](%s)[/COLOR]' %  year
            if lang != 'VOSE' and not config.get_setting('unify'):
                stitle += ' [COLOR gold][%s][/COLOR]' %  lang

        context = renumbertools.context(item)
        context2 = autoplay.context
        context.extend(context2)
        new_item= Item(channel=item.channel,
                       action='folders',
                       title=stitle,
                       url=url,
                       plot=type.capitalize(),
                       type=item.type,
                       thumbnail=thumbnail,
                       language = lang,
                       infoLabels={'year':year}
                       )
        if not type in ('anime', 'ova'):
            new_item.contentTitle=title
        else:
            new_item.contentSerieName=title
            new_item.context = context
        itemlist.append(new_item)

        # Paginacion
    next_page = scrapertools.find_single_match(data,
                                               '"page-item active">.*?</a>.*?<a class="page-link" href="([^"]+)">')

    if next_page != "":
        actual_page = scrapertools.find_single_match(item.url, '([^\?]+)?')
        itemlist.append(Item(channel=item.channel,
                             action="list_all",
                             title=">> Página siguiente",
                             url=actual_page + next_page,
                             thumbnail='https://s16.postimg.cc/9okdu7hhx/siguiente.png'
                             ))
    tmdb.set_infoLabels(itemlist, seekTmdb=True)
    return itemlist


def section(item):

    itemlist = []

    data = get_source(item.url)

    patron = '<a class="dropdown-item" href="(/%s/[^"]+)">([^<]+)</a>' % item.mode

    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, title in matches:
        itemlist.append(Item(channel=item.channel, title=title, url=host + url, action="list_all"))

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto
    try:
        if texto != '':
            return list_all(item)
        else:
            return []
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

def new_episodes(item):
    logger.info()

    itemlist = []
    infoLabels = dict()

    full_data = get_source(item.url)
    data = scrapertools.find_single_match(full_data, '<section class="caps">.*?</section>')
    patron = '<article.*?<a href="([^"]+)">.*?src="([^"]+)".*?'
    patron += 'class="vista2">([^<]+)</span>.*?'
    patron += '<span class="episode">.*?</i>([^<]+)</span>.*?<h2 class="Title">([^<]+)</h2>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, _type, epi, scrapedtitle in matches:
        _type = _type.strip().lower()
        url = scrapedurl
        lang, title = clear_title(scrapedtitle)
        
        season, episode = renumbertools.numbered_for_tratk(item.channel, title, 1, int(epi))
        
        scrapedtitle += " - %sx%s" % (season, str(episode).zfill(2))
        
        if lang != 'VOSE' and not config.get_setting('unify'):
            scrapedtitle += ' [COLOR gold][%s][/COLOR]' %  lang
        
        itemlist.append(Item(channel=item.channel, title=scrapedtitle, url=url, thumbnail=scrapedthumbnail,
                             action='findvideos', language=lang, plot=_type.capitalize(), type=_type,
                             contentSerieName=title, infoLabels=infoLabels))

    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

    return itemlist

def folders(item):
    logger.info()
    itemlist = []
    exf = list_epsxf.get(epsxfolder, None)
    if not epsxfolder:
        return episodesxfolder(item)
    data = get_source(item.url)
    patron = '<a class="item" href="([^"]+)">'
    matches = re.compile(patron, re.DOTALL).findall(data)
    l_matches = len(matches)
    if l_matches <= exf:
        return episodesxfolder(item)
    div = l_matches // exf
    res = l_matches % exf
    tot_div = div
    
    count = 1
    for folder in list(range(0, tot_div)):
        final = (count*exf)
        inicial = (final - exf) + 1
        if count == tot_div:
            final = (count*exf) + res
        
        title = "Eps %s - %s" % (inicial, final)
        init = inicial - 1
        itemlist.append(Item(channel=item.channel, title=title, url=item.url, infoLabels=item.infoLabels,
                             action='episodesxfolder', init=init, fin=final, type=item.type,
                             thumbnail=item.thumbnail, contentSerieName=item.contentSerieName,
                             foldereps=True))
        count += 1

    if item.contentSerieName != '' and config.get_videolibrary_support() and len(itemlist) > 0 and not item.extra == "epìsodios":
        itemlist.append(
            Item(channel=item.channel, title='[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]', url=item.url,
                 action="add_serie_to_library", extra="episodios", contentSerieName=item.contentSerieName,
                 extra1='library'))

    return itemlist

def episodios(item):
    logger.info()
    itemlist = []

    templist = folders(item)
    for tempitem in templist:
        itemlist += episodesxfolder(tempitem)

    return itemlist

def episodesxfolder(item):
    logger.info()
    itemlist = []
    if not item.init:
        item.init = None
    if not item.fin:
        item.fin = None
    data = get_source(item.url)
    patron = '<a class="item" href="([^"]+)">'
    matches = re.compile(patron, re.DOTALL).findall(data)
    infoLabels = item.infoLabels
    if item.init or item.fin:
        matches.reverse()
    for scrapedurl in matches[item.init:item.fin]:
        episode = scrapertools.find_single_match(scrapedurl, '.*?episodio-(\d+)')
        lang = item.language
        season, episode = renumbertools.numbered_for_tratk(item.channel, item.contentSerieName, 1, int(episode))
        title = "%sx%s - %s" % (season, str(episode).zfill(2),item.contentSerieName)
        url = scrapedurl
        infoLabels['season'] = season
        infoLabels['episode'] = episode

        itemlist.append(Item(channel=item.channel, title=title, contentSerieName=item.contentSerieName, url=url,
                             action='findvideos', language=lang, infoLabels=infoLabels))

    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

    itemlist = itemlist[::-1]
    if item.contentSerieName != '' and config.get_videolibrary_support() and len(itemlist) > 0 and not item.foldereps:
        itemlist.append(
            Item(channel=item.channel, title='[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]', url=item.url,
                 action="add_serie_to_library", extra="episodios", contentSerieName=item.contentSerieName,
                 extra1='library'))

    if item.init or item.fin:
        itemlist.reverse()
    return itemlist


def findvideos(item):
    logger.info()

    itemlist = []
    g_host = 'https://192-99-219-204.sysdop.com/'

    data = get_source(item.url)
    patron = r'%sreproductor\?url=([^&]+)' % host
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl in matches:
        server = ''
        scrapedurl = urllib.unquote(scrapedurl)
        
        if "cl?url=" in scrapedurl:
            scrapedurl = scrapertools.find_single_match(scrapedurl, '\?url=(.*)')
            url = g_host + scrapedurl.replace('+', '%20')
            check = httptools.downloadpage(url, only_headers=True, ignore_response_code=True).code

            if check != 200: 
                continue
            server = "directo"
        
        elif '?url=' in  scrapedurl:
            url = scrapertools.find_single_match(scrapedurl, '.*?url=([^&]+)?')
        else:
            url = scrapedurl
            

        if url:
            itemlist.append(Item(channel=item.channel, title='%s', url=url, action='play',
                                 language = item.language, infoLabels=item.infoLabels, server=server))

    itemlist = servertools.get_servers_itemlist(itemlist, lambda x: x.title % x.server.capitalize())

    if __comprueba_enlaces__:
        itemlist = servertools.check_list_links(itemlist, __comprueba_enlaces_num__)

    # Requerido para FilterTools

    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    if config.get_videolibrary_support() and itemlist > 0 and item.extra != 'findvideos' and not item.contentSerieName:
        itemlist.append(Item(channel=item.channel, title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
                             url=item.url, action="add_pelicula_to_library", extra="findvideos",
                             contentTitle=item.contentTitle))

    return itemlist

def newest(categoria):
    itemlist = []
    item = Item()
    if categoria == 'anime':
        item.url=host
        itemlist = new_episodes(item)
    return itemlist

def clear_title(title):
    if 'latino' in title.lower():
        lang = 'Latino'
    elif 'castellano' in title.lower():
        lang = 'Castellano'
    else:
        lang = 'VOSE'
    
    title = re.sub(r'Audio|Latino|Castellano|\((.*?)\)', '', title)
    title = re.sub(r'\s:', ':', title)

    return lang, title

