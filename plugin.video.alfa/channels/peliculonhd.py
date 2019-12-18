# -*- coding: utf-8 -*-
# -*- Channel PeliculonHD -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import re, urllib
from lib import jsunpack
from core import tmdb
from core import httptools
from core.item import Item
from core import servertools
from core import scrapertools
from bs4 import BeautifulSoup
from channelselector import get_thumb
from platformcode import config, logger
from channels import filtertools, autoplay

IDIOMAS = {'espanol': 'CAST', 'castellano': 'CAST', 
           'latino': 'LAT', 'subtitulado': 'VOSE'}
list_language = IDIOMAS.values()
list_quality = []
list_servers = ['fembed', 'videofiles', 'rapidvideo', 'oprem', 'jawcloud']

host = "https://www.peliculonhd.tv/"

unify = config.get_setting('unify')


def mainlist(item):
    logger.info()

    itemlist = []

    autoplay.init(item.channel, list_servers, list_quality)


    itemlist.append(Item(channel=item.channel, title='Peliculas',
                         url=host+'pelicula',
                         action='list_all',
                         thumbnail= get_thumb('movies', auto=True)))
    
    itemlist.append(Item(channel=item.channel, title='Series', 
                         url=host+'serie',
                         action='list_all',
                         thumbnail= get_thumb('tvshows', auto=True)))

    itemlist.append(Item(channel=item.channel, title='Por Generos', action='section',
                         thumbnail=get_thumb('genres', auto=True), _id='4709'))
    
    itemlist.append(Item(channel=item.channel, title='Por Año', action='section',
                         thumbnail=get_thumb('year', auto=True), _id='21052'))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search",
                         url=host + '?s=', thumbnail=get_thumb("search", auto=True)))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def create_soup(url, post=None, headers=None):
    logger.info()

    data = httptools.downloadpage(url, post=post, headers=headers).data

    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")

    return soup

def get_tmdb_thumb(img_url):
    original = re.sub(r'p/w\d+', 'p/original', img_url)
    f_thumb = re.sub('(.*?)/original', '', original)
    filtro_tmdb = {"poster_path": f_thumb}.items()
    return original, filtro_tmdb

def section(item):
    logger.info()
    itemlist=[]    
    
    soup = create_soup(host).find("li", id="menu-item-%s" % item._id)

    
    matches = soup.find_all('a')

    for elem in matches[1:]:
        title = elem.text
        plot=''
        url = elem['href']
        if title.lower() == 'eroticas' and config.get_setting('adult_mode') == 0:
            continue
        if not url.startswith('http'):
            url = host+url
        if title.lower() != 'proximamente':
            itemlist.append(Item(channel=item.channel, url=url, title=title,
                                 plot=plot, action='list_all',
                                 type=item.type))

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto
    item.first = 0
    if texto != '':
        return search_results(item)
    else:
        return []

def search_results(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)

    for elem in soup.find_all("div", class_="result-item"):

        url = elem.a["href"]
        thumb, o = get_tmdb_thumb(elem.img["src"])
        title = elem.img["alt"]
        year = elem.find("span", class_="year").text
        

        ctitle = title.partition(' | ')[0]
        
        if not unify:
            title += ' [COLOR darkgrey](%s)[/COLOR]' % year
        
        new_item = Item(channel=item.channel, title=title, url=url,
                        action='findvideos', thumbnail=thumb, infoLabels = {'year': year})
        
        if '/pelicula' in url:
            new_item.contentTitle = ctitle
        else:
            new_item.contentSerieName=ctitle
            new_item.action = 'seasons'

        itemlist.append(new_item)

    tmdb.set_infoLabels_itemlist(itemlist, True)
    return itemlist


def list_all(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url).find("div", class_="content")

    matches = soup.find_all("article", id=re.compile(r"^post-\d+"))

    for elem in matches:

        info_1 = elem.find("div", class_="poster")
        info_2 = elem.find("div", class_="data")

        thumb, filto_tmdb = get_tmdb_thumb(info_1.img["src"])
        title = info_1.img["alt"]

        url = info_1.a["href"]
        year = scrapertools.find_single_match(info_2.find("span").text, r"\d{4}")
        rating = info_1.find('div', class_='rating').text.strip() or '--'
        
        ctitle = title.partition(' | ')[0]
        if not unify:
            title += ' [COLOR blue](%s)[/COLOR] [COLOR gold](%s)[/COLOR]' % (year, rating)
        
        new_item = Item(channel=item.channel, title=title, url=url,
                        action='findvideos', thumbnail=thumb,
                        infoLabels = {'year': year})
        
        if '/pelicula' in url:
            new_item.contentTitle = ctitle
        else:
            new_item.contentSerieName=ctitle
            new_item.action = 'seasons'

        itemlist.append(new_item)



    tmdb.set_infoLabels_itemlist(itemlist, True)

    
    try:
        url_next_page = soup.find("a", class_="arrow_pag")["href"]
    except:
        return itemlist

    if url_next_page:
        url_next_page = '%s' % url_next_page
        itemlist.append(Item(channel=item.channel, title="Siguiente >>",
                             url=url_next_page, action='list_all'))

    return itemlist


def seasons(item):
    logger.info()

    itemlist=[]
    infoLabels = item.infoLabels

    soup = create_soup(item.url).find("div", id="seasons")
    matches = soup.find_all('span', class_='title')

    
    for elem in matches:
        season = scrapertools.find_single_match(elem.text, r'emporada (\d+)')
        infoLabels['season'] = season
        title = 'Temporada %s' % season
        itemlist.append(Item(channel=item.channel, title=title, url=item.url,
                             action='episodesxseasons', infoLabels=infoLabels))
    
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'episodios':
        itemlist.append(
                Item(channel=item.channel, title='Añadir esta serie a la videoteca',
                     url=item.url, action="add_serie_to_library", extra="episodios",
                     contentSerieName=item.contentSerieName, text_color='yellow'))

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
    
    i = int(infoLabels['season']) - 1
    soup = create_soup(item.url).find_all('div', class_='se-a')[i]
    matches = soup.find_all('li')

    for elem in matches:
        info = elem.a

        thumb = elem.img['src']
        stitle = info.text
        url = info['href']
        sepisode = elem.find('div', class_='numerando').text.partition(' - ')[2]

        infoLabels['episode'] = sepisode
        title = '%sx%s - %s' % (infoLabels['season'], sepisode, stitle)

        itemlist.append(Item(channel=item.channel, title= title, url=url,
                             action='findvideos', infoLabels=infoLabels))

    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

    return itemlist


def findvideos(item):
    logger.info()
    
    itemlist = []
    infoLabels = item.infoLabels
    servers = {'premium': 'oprem'}
    
    soup = create_soup(item.url)
    matches = soup.find_all('li', id=re.compile(r'player-option-\d+'))
    stitle = ''

    for elem in matches:

        lang = elem.find('span', class_='title').text.lower()
        language = IDIOMAS.get(lang, lang)

        if not unify:
            stitle = '[COLOR darkgrey][%s][/COLOR] ' % language
        
        _type = elem['data-type']
        nume = elem['data-nume']
        _id = elem['data-post']
        post = {'action': 'doo_player_ajax', 'post': _id, 'nume': nume, 'type':_type}

        post_url = '%swp-admin/admin-ajax.php' % host
        new_soup = create_soup(post_url, post=post, headers={'Referer': item.url})
        
        scrapedurl = new_soup.iframe['src']
        #modo viejo
        if 'play.php' in scrapedurl:
            try:
                data = httptools.downloadpage(scrapedurl, headers={'Referer': item.url}).data
                enc_data = scrapertools.find_single_match(data, '(eval.*?)</script')
                
                dec_data = jsunpack.unpack(enc_data)
                url = scrapertools.find_single_match(dec_data, 'src="([^"]+)"')
                
                server = servertools.get_server_from_url(url)
                title = stitle + server.capitalize()
                
                itemlist.append(Item(channel=item.channel, url=url, title=title, action='play',
                                    language=language, infoLabels=infoLabels, server=server))

            except:
                continue
        #modo menos viejo
        elif 'xyz' in scrapedurl:
            new_data = httptools.downloadpage(scrapedurl, headers={'Referer': item.url}).data
            patron = r"addiframe\('([^']+)'"
            matches = scrapertools.find_multiple_matches(new_data, patron)

            for new_url in matches:
                if 'play.php' in new_url:
                    
                    data = httptools.downloadpage(new_url).data
                    enc_data = scrapertools.find_single_match(data, '(eval.*?)</script')

                    try:
                        dec_data = jsunpack.unpack(enc_data)                    
                    except:
                        continue
                    
                    url = scrapertools.find_single_match(dec_data, r'src\s*=\s*"([^"]+)"')
                    if 'vev.' in url:
                        continue
                
                elif 'embedvip' in new_url:
                    continue
                
                if url != '':
                    server = servertools.get_server_from_url(url)
                    title = stitle + server.capitalize()
                    
                    itemlist.append(Item(channel=item.channel, url=url, title=title, action='play',
                                    language=language, infoLabels=infoLabels, server=server))

        #modo nuevo
        else:
            try:
                soup = create_soup(scrapedurl, headers={'Referer': item.url})
            except:
                continue
            matches = soup.find_all('li', class_='option servers')
            from urlparse import urlparse
            i = urlparse(scrapedurl)
            url = 'https://%s/edge-data/' % (i[1])

            for elem in matches:
                srv = elem['title'].lower()
                if 'vip' in srv: continue
                st = elem['data-embed']
                vt = elem['data-issuer']
                tk = elem['data-signature']

                post = {'streaming':st, 'validtime':vt, 'token':tk}
                server = servers.get(srv, srv)
                title = stitle + server.capitalize()

                itemlist.append(Item(channel=item.channel, url=url, title=title, action='play',
                                    language=language, infoLabels=infoLabels, server=server,
                                     _post=post, _ref={'Referer': scrapedurl}))

    itemlist = filtertools.get_links(itemlist, item, list_language)
    autoplay.start(itemlist, item)

    itemlist = sorted(itemlist, key=lambda it: it.language)

    if item.contentType != 'episode':
        if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos':
            itemlist.append(
                Item(channel=item.channel, title='Añadir esta pelicula a la videoteca',
                     url=item.url, action="add_pelicula_to_library", extra="findvideos",
                     contentTitle=item.contentTitle, text_color='yellow'))

    return itemlist

def play(item):
    logger.info()
    if item._post:
        post = urllib.urlencode(item._post)
        try:
            data = httptools.downloadpage(item.url, post=post, headers=item._ref).json
            item.url = data.get('url', '')
            
            if 'peliculonhd' in item.url:
                url = item.url.replace('embed/', 'hls/')
                if not url.endswith('.m3u8'):
                    url += '.m3u8'
                data = httptools.downloadpage(url).data
                new_url = scrapertools.find_single_match(data, '(/mpegURL.*)')
                item.url = 'https://videos.peliculonhd.com%s' % new_url
                return [item]

            item.server = servertools.get_server_from_url(item.url)
        
        except:
            logger.error('Error get link %s' % item.url)
            item.url = ''

    return [item]
