# -*- coding: utf-8 -*-

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, jsontools
import sys

if sys.version_info[0] >= 3:
    from urllib.parse import quote
else:
    from urllib import quote

host = "https://beeg.com/"

perpage = 30


def get_api_key():
    data = httptools.downloadpage(host, headers={'User-agent': httptools.get_user_agent()}).data
    url = scrapertools.find_single_match(data, '<link href="(\/js\/app\.[a-zA-Z0-9_]+\.js)"')
    data2 = httptools.downloadpage(host[:-1] + url, headers={'User-agent': httptools.get_user_agent()}).data
    url_api = scrapertools.find_single_match(data2, 'r="([^"]+)",')

    # ~ logger.info(url_api)
    config.set_setting('url_api', url_api, 'beeg')


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    if not config.get_setting('url_api', 'beeg'):
        get_api_key()

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    if descartar_xxx: return itemlist
    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False:
            return itemlist
    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = "index/main/0/pc", cod_value='videos', page=0 ))

    itemlist.append(item.clone( title = 'Por canal', action = 'list_all', url = 'channels?offset=0', cod_value='channels', page=0 ))
    itemlist.append(item.clone( title = 'Por categoría', action = 'list_all', url = 'tags', cod_value='tags', page=0 ))
    itemlist.append(item.clone( title = 'Por estrella', action = 'list_all', url = 'people?offset=0', cod_value='people', page=0 ))

    itemlist.append(item.clone( title = 'Buscar vídeo ...', action = 'search', search_type = 'movie' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not config.get_setting('url_api', 'beeg'):
        get_api_key()

    url = "https://api.beeg.com/api/v6/%s/%s" % (config.get_setting('url_api', 'beeg'), item.url)
    data = httptools.downloadpage(url).data
    jdata = jsontools.load(data)

    cat = item.cod_value
    num_matches = len(jdata[cat])

    for match in jdata[cat][item.page * perpage:]:
        if cat == 'videos':
            start = scrapertools.find_single_match(str(match), "'start': (.*?),")
            if start == None: start = 'null'

            end = scrapertools.find_single_match(str(match), "'end': (.*?),")
            if end == None: end = 'null'

            url = "https://beeg.com/api/v6/%s/video/%s?v=2&s=%s&e=%s" % (config.get_setting('url_api', 'beeg'), match['svid'], start, end)
            itemlist.append(item.clone( action = 'findvideos', url = url, title = match['title'] if match['title'] else match['ps_name'], thumbnail = 'http://img.beeg.com/264x198/4x3/%s' % match['thumbs'][0]['image'] ))
        elif cat == 'people':
            url = "index/people/0/pc?search_mode=code&people=%s" %(match['code'])
            itemlist.append(item.clone( action = 'list_all', cod_value='videos', url = url, page=0, title = match['name'], thumbnail = 'https://thumbs.beeg.com/img/cast/%s.png/to.jpg?a=1x1&w=150' % match['id'] ))
        elif cat == 'channels':
            url = "index/channel/0/pc?channel=%s" %(match['channel'])
            itemlist.append(item.clone( action = 'list_all', cod_value='videos', url = url, page=0, title = match['ps_name'], thumbnail = 'https://thumbs.beeg.com/channels/%s.png/to.jpg?a=1x1&w=150' % match['id'] ))
        elif cat == 'tags':
            url = "index/tag/0/pc?tag=%s" %(quote(match['tag']))
            itemlist.append(item.clone( action = 'list_all', cod_value='videos', url = url, page=0, title = match['tag'].capitalize()))

        if len(itemlist) >= perpage:  break

    buscar_next = True
    if num_matches > perpage: # subpaginación interna dentro de la página si hay demasiados items
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title = '>> Página siguiente', page = item.page + 1, action = 'list_all', text_color = 'coral' ))
            buscar_next = False

    if buscar_next:
        if itemlist:
            if cat == 'videos':
                try:
                    prepage = int(item.url.split("main/")[1].split("/pc")[0])
                    page = prepage + 1
                    next_url = "index/main/%s/pc" %(str(page))
                except: next_url = ''    
            elif cat == 'people' and not "search_mode" in item.url:
                prepage = int(item.url.split("?offset=")[1])
                page = prepage + 100
                next_url = "people?offset=%s" %(str(page))
            elif cat == 'channels':
                prepage = int(item.url.split("?offset=")[1])
                page = prepage + 100
                next_url = "channels?offset=%s" %(str(page))  
            if next_url:
                itemlist.append(item.clone( title = '>> Página siguiente', url = next_url, action = 'list_all', page = 0, text_color = 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    try:
        data = httptools.downloadpage(item.url).data
    except: return []        
    jdata = jsontools.load(data)
    for match in jdata:
        if match[0].isdigit():
            url = jdata[match]
            if url is None: continue
            if not url.startswith("http"):
                url = "https:" + url
            if "{DATA_MARKERS}" in url:
                url = url.replace("{DATA_MARKERS}", "data=pc.ES")
            itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', quality = match, url = url, language = 'VO' ))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    json_data = jsontools.load(httptools.downloadpage(item.url).data)

    for match in json_data['items']:
        if match['type'] == "people":
            url = "index/people/0/pc?search_mode=code&people=%s" %(match['code'])
            thumbnail = 'https://thumbs.beeg.com/img/cast/%s.png/to.jpg?a=1x1&w=150' % match['id']
            itemlist.append(item.clone( action = 'list_all', url = url, cod_value='videos', thumbnail=thumbnail, title = match['name'].capitalize(), page = 0))
        elif match['type'] == 'tag':
            url = "index/tag/0/pc?tag=%s" %(quote(match['code']))  
            thumbnail = 'https://thumbs.beeg.com/img/cast/%s.png/to.jpg?a=1x1&w=150' % match['id']
            itemlist.append(item.clone( action = 'list_all', url = url, cod_value='videos', title = match['name'].capitalize(), page = 0))
        elif match['type'] == 'channel':
            url = "index/channel/0/pc?channel=%s" %(match['code'])
            thumbnail = 'https://thumbs.beeg.com/img/cast/%s.png/to.jpg?a=1x1&w=150' % match['id']
            itemlist.append(item.clone( action = 'list_all', url = url, cod_value='videos', thumbnail=thumbnail, title = match['name'].capitalize(), page = 0))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url =  host + "api/v6/%s/suggest?q=%s" % (config.get_setting('url_api', 'beeg'), texto.replace(" ", "+"))
        return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
