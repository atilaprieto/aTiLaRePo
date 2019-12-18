# -*- coding: utf-8 -*-
# -*- Channel Xdede -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import re
import urllib
from channelselector import get_thumb
from core import httptools
from core import jsontools
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item
from channels import filtertools
from channels import autoplay
from platformcode import config, logger

unify = config.get_setting('unify')

IDIOMAS = {'1':'CAST', '2':'LAT', '3':'VOSE', '4':'VO'}
list_language = IDIOMAS.values()


list_quality = ['Oficial', '1080p', '720p', '480p', '360p']

list_servers = ['fembed', 'vidcloud','clipwatching', 'gamovideo']

host = 'https://movidy.co/'

def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = []

    itemlist.append(Item(channel=item.channel, title='Peliculas', action='sub_menu', type='peliculas',
                         thumbnail= get_thumb('movies', auto=True)))
    
    itemlist.append(Item(channel=item.channel, title='Series', action='sub_menu', type='series',
                         thumbnail= get_thumb('tvshows', auto=True)))

    itemlist.append(Item(channel=item.channel, title='Animes', action='sub_menu', type='animes',
                         thumbnail= get_thumb('anime', auto=True)))
    
    itemlist.append(Item(channel=item.channel, title='Colecciones', action='list_collections',
                        url= host+'listas', thumbnail=get_thumb('colections', auto=True)))
    
    itemlist.append(Item(channel=item.channel, title='Buscar...', action="search",
                         url=host + 'search?go=', thumbnail=get_thumb("search", auto=True)))

    autoplay.show_option(item.channel, itemlist)

    return itemlist

def sub_menu(item):
    logger.info()

    itemlist=[]

    url_estreno = host + item.type + '/novedades'
    
    if item.type == 'peliculas':
        url_estreno = host + item.type + '/estrenos'
        itemlist.append(Item(channel=item.channel, title='Estrenos', url=url_estreno, action='list_all',
                         thumbnail=get_thumb('estrenos', auto=True), type=item.type))
    else:
        itemlist.append(Item(channel=item.channel, title='Nuevos Capitulos', url=url_estreno, action='list_all',
                         thumbnail=get_thumb('new episodes', auto=True), type=item.type))

    itemlist.append(Item(channel=item.channel, title='Novedades', url=host+item.type, action='list_all',
                         thumbnail=get_thumb('newest', auto=True), type=item.type))
    
    itemlist.append(Item(channel=item.channel, title='Actualizadas', url=host+'/actualizado/'+item.type,
                         action='list_all', thumbnail=get_thumb('updated', auto=True), type=item.type))
    
    itemlist.append(Item(channel=item.channel, title='Mejor Valoradas', url=host+item.type+'/mejor-valoradas',
                         action='list_all', thumbnail=get_thumb('more voted', auto=True), type=item.type))
    
    itemlist.append(Item(channel=item.channel, title='Genero', action='section',
                         thumbnail=get_thumb('genres', auto=True), type=item.type))
    
    itemlist.append(Item(channel=item.channel, title='Por Año', action='section',
                         thumbnail=get_thumb('year', auto=True), type=item.type))

    return itemlist

def get_source(url, referer=None):
    logger.info()
    if referer is None:
        data = httptools.downloadpage(url).data
    else:
        data = httptools.downloadpage(url, headers={'Referer':referer}).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    return data

def section(item):
    logger.info()
    itemlist=[]
    if 'Genero' in item.title:
        list_genre = {"Acción","Animación","Bélica","Ciencia ficción",
                      "Comedia","Crimen","Drama","Familia","Misterio",
                      "Música","Romance","Suspense","Terror","Wester"}
        for name in list_genre:
            url = '%s%s/filtro/%s,/,' % (host, item.type, name)
            
            itemlist.append(Item(channel=item.channel, url=url, title=name,
                                 action='list_all', type=item.type))
    else:
        try:
            import datetime
            now = datetime.datetime.now()
            c_year = now.year + 1
        except:
            c_year = 2020
        l_year = c_year - 19
        year_list = range(l_year, c_year)

        for year in year_list:
            year = str(year)
            url = '%s%s/filtro/,/%s,' % (host, item.type, year)
            
            itemlist.append(Item(channel=item.channel, title=year, url=url,
                                 action="list_all", type=item.type))
        itemlist.reverse()
        itemlist.append(Item(channel=item.channel, title='Introduzca otro año...', url='',
                                 action="year_cus", type=item.type))

    return itemlist

def year_cus(item):
    from platformcode import platformtools
    heading = 'Introduzca Año (4 digitos)'
    year = platformtools.dialog_numeric(0, heading, default="")
    item.url = '%s%s/filtro/,/%s,' % (host, item.type, year)
    item.action = "list_all"
    if year and len(year) == 4:
        return list_all(item)

def list_all(item):
    logger.info()
    itemlist = []

    data = get_source(item.url)
    patron = '<article class="Cards.*?href="([^"]+)"(.*?)<img.*?'
    patron += 'data-echo="([^"]+)" alt="([^"]+)"'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedinfo, scrapedthumbnail, scrapedtitle in matches:

        title = scrapedtitle
        scrapedtitle = re.sub(r' \((.*?)\)$', '', scrapedtitle)
        thumbnail = scrapedthumbnail.strip()
        url = scrapedurl
        tmdb_id = scrapertools.find_single_match(url, r'/\w(\d+)-')
        

        thumbnail = re.sub(r'p/w\d+', 'p/original', thumbnail)
        
        if item.type == 'search':
            s_title =  scrapertools.find_single_match(url, host+'(\w+)')
            if not unify:
                title += ' [COLOR grey][I](%s)[/I][/COLOR]' % s_title.capitalize()[:-1]
        
        new_item = Item(channel=item.channel,
                        title=title,
                        url=url,
                        thumbnail=thumbnail,
                        infoLabels={'tmdb_id':tmdb_id})

        if item.type == 'peliculas' or 'peliculas' in url:
            new_item.action = 'findvideos'
            new_item.contentTitle = scrapedtitle
            new_item.type = 1
            
            calidad_baja = scrapertools.find_single_match(scrapedinfo, r'>(\w+\s\w+)</div>$')
            
            if calidad_baja:
                new_item.title += '[COLOR tomato] (Calidad Baja)[/COLOR]'
        else:
            new_item.action = 'seasons'
            new_item.contentSerieName = scrapedtitle
            new_item.type = 0
            
            sesxep = scrapertools.find_single_match(url, r'/(\d+x\d+)$')
            
            if sesxep:
                new_item.title += ' '+sesxep
                new_item.action = 'findvideos'
            

        itemlist.append(new_item)

    tmdb.set_infoLabels(itemlist, seekTmdb=True)
    if item.type == 'search':
        itemlist.sort (key=lambda i: (i.type, i.title))
    #  Paginación

    url_next_page = scrapertools.find_single_match(data,'<a href="([^"]+)" up-target="body">Pagina s')
    if url_next_page:
        itemlist.append(item.clone(title="Siguiente >>", url=url_next_page, action='list_all', text_color='gold'))

    return itemlist

def list_collections(item):
    logger.info()

    itemlist = []

    data = get_source(item.url)
    patron = '<article>(.*?)href="([^"]+)".*?<h2>([^<]+)</h2><p>([^<]+)</p>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for thumb, url, title, plot in matches:
        thumbnail = scrapertools.find_single_match(thumb, '<img src="([^"]+)">')
        if thumbnail:
            thumb = re.sub('p/w\d+', 'p/original', thumbnail)
        else:
            thumb = 'https://i.imgur.com/P4g4aW2.png'

        itemlist.append(Item(channel=item.channel, action='list_all', title=title, url=url, thumbnail=thumb, plot=plot))

    url_next_page = scrapertools.find_single_match(data, '<link rel="next" href="([^"]+)"')
    if url_next_page:
        itemlist.append(item.clone(title="Siguiente >>", url=url_next_page, action='list_collections'))
    return itemlist


def seasons(item):
    logger.info()

    itemlist=[]

    data = get_source(item.url)
    patron = "activeSeason\(this,'temporada-(\d+)'"
    matches = re.compile(patron, re.DOTALL).findall(data)

    infoLabels = item.infoLabels
    for season in matches:
        infoLabels['season']=season
        title = 'Temporada %s' % season
        itemlist.append(Item(channel=item.channel, title=title, url=item.url, action='episodesxseasons',
                             infoLabels=infoLabels))
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

    if config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(
                Item(channel=item.channel, title='[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]', url=item.url,
                     action="add_serie_to_library", extra="episodios", contentSerieName=item.contentSerieName))

    return itemlist

def episodios(item):
    logger.info()
    itemlist = []
    templist = seasons(item)
    for tempitem in templist:
        itemlist += episodesxseasons(tempitem)

    return itemlist

def episodesxseasons(item):
    logger.info()

    itemlist = []
    infoLabels = item.infoLabels

    data=get_source(item.url)
    
    pat = '<div class="season temporada-%s(.*?)</a></li></div>' % item.infoLabels['season']
    data = scrapertools.find_single_match(data, pat)
    
    patron= '<li ><a href="([^"]+)"(.*?)'
    patron += r'<h2>([^>]+)</h2>.*?<span>\d+ - (\d+)</span>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, sthumbnail, scrapedtitle, ep in matches:
        thumbnail = scrapertools.find_single_match(sthumbnail, 'data-echo="([^"]+)"')
        thumb = re.sub(r'p/w\d+', 'p/original', thumbnail)
        infoLabels['episode'] = ep
        
        title = '%sx%s - %s' % (infoLabels['season'], infoLabels['episode'], scrapedtitle)

        itemlist.append(Item(channel=item.channel, title=title, url=url, action='findvideos',
                             infoLabels=infoLabels, thumbanil=thumb))

    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

    return itemlist

def findvideos(item):
    logger.info()

    itemlist = []
    itemlist2 = []
    headers = {'Referer': item.url}

    server_url = {'gamovideo': 'http://gamovideo.com/embed-%s.html',
                  'gounlimited': 'https://gounlimited.to/embed-%s.html',
                  'streamplay': 'https://streamp1ay.me/player-%s.html',
                  'powvideo': 'https://powvldeo.net/iframe-%s-1536x701.html',
                  'vidcloud': 'https://vidcloud.co/player?fid=%s&page=embed',
                  'vidlox': 'https://vidlox.me/embed-%s.html',
                  'clipwatching': 'https://clipwatching.com/embed-%s.html',
                  'jetload': 'https://jetload.net/e/%s',
                  'mixdrop': 'https://mixdrop.co/e/%s'
                  }

    data = get_source(item.url)
    s_id = scrapertools.find_single_match(data, r'id="loadVideos".*?secid="(\w\d+)"')

    if s_id:
        import requests
        url = host + 'json/loadVIDEOS'
        header = {'User-Agent': 'Mozilla/5.0 (Android 10; Mobile; rv:70.0) Gecko/70.0 Firefox/70.0'}
        session = requests.Session()
        page = session.post(url, data={'id': s_id}, headers=header).json()

        if page.get('status', '') == 200:
            data2 = page['result']
            patron = r"C_One\(this, (\d+), '([^']+)'.*?"
            patron += r'src=".*?/img/(\w+)'
            matches = re.compile(patron, re.DOTALL).findall(data2)
            for language, url, server in matches:
                
                req = httptools.downloadpage(url, headers=headers, follow_redirects=False)
                location = req.headers.get('location', None)


                if location:
                    url = location
                else:
                    new_data = req.data.replace("'", '"')
                    url = scrapertools.find_single_match(new_data, 'file": "([^"]+)"')
                if not url:
                     continue             
                try:
                    server = server.split(".")[0]
                except:
                    server= ""

                if 'betaserver' in server:
                    server = 'directo'

                lang = IDIOMAS.get(language, 'VO')

                quality = 'Oficial'

                title = '%s [%s] [%s]' % (server.capitalize(), lang, quality)

                itemlist.append(Item(channel=item.channel, title=title, url=url, action='play', language=lang,
                                 quality=quality, server=server, headers=headers, infoLabels=item.infoLabels,
                                 p_lang=language))

    patron = '<li><a href="([^"]+)".*?<img.*?>([^<]+)<b>([^<]+)<.*?src="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, server, quality, language in matches:
        if '/sc_' in url:
            continue
        if url != '':

            try:
                server = server.split(".")[0].replace('1', 'l')
            except:
                continue

            _id = scrapertools.find_single_match(url, r'link/\w+_(.*)')

            url = server_url.get(server, url)
            
            if not url.startswith(host):
                url = url % _id
            
            language = scrapertools.find_single_match(language, r'/(\d+)\.png')
            lang = IDIOMAS.get(language, 'VO')
            
            title = '%s [%s] [%s]' % (server.capitalize(), lang, quality)
            
            itemlist2.append(Item(channel=item.channel, title=title, url=url, action='play', language=lang,
                                 quality=quality, server=server, headers=headers, infoLabels=item.infoLabels,
                                 p_lang=language))

    
    itemlist2.sort(key=lambda i: (i.p_lang, i.server))
    
    itemlist.extend(itemlist2)

    if not itemlist:
        itemlist.append(Item(channel=item.channel, folder=False, text_color='tomato',
                            title='[I] Aún no hay enlaces disponibles [/I]'))
        return itemlist
    
    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    
    return itemlist


def play(item):
    logger.info()
    
    if item.url.startswith(host):
        item.url = httptools.downloadpage(item.url, headers=item.headers, only_headers=True).url
    
    return [item]




def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto
    item.type = 'search'
    if texto != '':
        try:
            return list_all(item)
        except:
            import sys
            for line in sys.exc_info():
                logger.error("{0}".format(line))
            return []
    else:
        return []

def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    try:
        if categoria in ['peliculas']:
            item.url = host + 'peliculas'
        elif categoria == 'infantiles':
            item.url = host + 'peliculas/filtro/Animación,/,'
        elif categoria == 'terror':
            item.url = host + 'peliculas/filtro/Terror,/,'
        item.type='peliculas'
        itemlist = list_all(item)
        if itemlist[-1].title == 'Siguiente >>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist
