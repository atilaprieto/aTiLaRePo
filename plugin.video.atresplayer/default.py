import sys
import xbmcgui
import xbmcplugin
import xbmc
import urllib
import urllib2
import urlparse
import json
import xbmcaddon
import os
import re
import random
import requests
import unicodedata
from lib import youtube_dl
from sqlite3 import dbapi2 as database
from types import UnicodeType
from F4mProxy import f4mProxyHelper
 
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
my_addon = xbmcaddon.Addon()
PATH = my_addon.getAddonInfo('path')
sys.path.append(xbmc.translatePath(os.path.join(PATH, 'lib')))

cache_location = os.path.join(xbmc.translatePath("special://database"), 'atresplayer.db')
dbcon = database.connect(cache_location)
dbcur = dbcon.cursor()

def strip_accents(text):
    try:
        text = unicode(text.encode("utf-8"), 'utf-8')
    except NameError:
        pass
    text = unicodedata.normalize('NFD', text)\
           .encode('ascii', 'ignore')\
           .decode("utf-8")
    return str(text)

def only_legal_chars(string_in):
    string_out = strip_accents(string_in)
    string_out = re.sub(r'[#\\/:"*?<>|]+', "", string_out)
    string_out = "".join(i for i in string_out if ord(i)<128)
    string_out = ' '.join(string_out.split())
    return string_out

def utf8me(string_in):
    return safe_unicode(string_in).encode('utf-8')

def safe_unicode(value):
    if type(value) is UnicodeType:
        return value
    else:
        try:
            return unicode(value, 'utf-8')
        except:
            return unicode(value, 'iso-8859-1')
 
def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

def get_video_url(page_url, repeat):

    if repeat == 3:
        return ''
    else:

        method2 = 0

        page_url = page_url.replace(' ', '%20')

        dbcur.execute("CREATE TABLE IF NOT EXISTS links (page_link TEXT, return_link TEXT, UNIQUE(page_link));")
        dbcon.commit()

        dbcur.execute("SELECT return_link FROM links WHERE page_link = '" + page_url + "'")
        match = dbcur.fetchone()
        if match != None:
            xbmc.sleep(750)
            return match[0]
        else:
            if my_addon.getSetting('username') == '' or my_addon.getSetting('password') == '':
                method2 = 1
            else:
                try:
                    ydl = youtube_dl.YoutubeDL({'outtmpl': u'%(id)s%(ext)s', 'username':my_addon.getSetting('username'), 'password':my_addon.getSetting('password')})
                    result = ydl.extract_info(page_url, download=False)
                    if 'entries' in result:
                        video = result['entries'][0]
                    else:
                        video = result

                    dumped = json.dumps(video)

                    a = dumped.split('.m3u8')
                    b = a[len(a)-2].split('"')
                    c = a[len(a)-1].split('"')
                    final_video = b[len(b)-1] + '.m3u8'

                    dbcur.execute("INSERT INTO links VALUES ('" + page_url + "', '" + final_video + "');")
                    dbcon.commit()

                    return final_video

                except Exception as e:
                    method2 = 1

            if method2 == 1:

                hs = {
                    'Sec-Fetch-Mode': 'cors',
                    'Origin': 'https://eljaviero.com',
                    'Accept-Language': 'es-ES,es;q=0.9',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Connection': 'keep-alive',
                    'Pragma': 'no-cache',
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Accept': '*/*',
                    'Cache-Control': 'no-cache',
                    'Referer': 'https://eljaviero.com/descargarvideosdelatele/download/',
                    'Sec-Fetch-Site': 'same-origin'
                }

                ds = urllib.urlencode({
                    'url_noticia': page_url,
                    'submit_enviar_url': 'ok',
                    'current_url': 'https://eljaviero.com/descargarvideosdelatele/download/'
                })
                
                request = urllib2.Request("https://eljaviero.com/descargarvideosdelatele/index.php", data=ds, headers=hs)
                data = json.loads(urllib2.urlopen(request, timeout = 60).read())

                if 'prueba de nuevo' in data['mensaje']:
                    repeat = repeat + 1
                else:
                    a = data['mensaje'].split('.f4m</div>')
                    b = a[0].split('>')

                    final_url = b[-1] + '.f4m'

                    if final_url == '.f4m':

                        a = data['mensaje'].split('<a href="')
                        b = a[3].split('"')

                        hs = {
                            'Sec-Fetch-Mode': 'cors',
                            'Origin': 'https://eljaviero.com',
                            'Accept-Language': 'es-ES,es;q=0.9',
                            'X-Requested-With': 'XMLHttpRequest',
                            'Connection': 'keep-alive',
                            'Pragma': 'no-cache',
                            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
                            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                            'Accept': '*/*',
                            'Cache-Control': 'no-cache',
                            'Referer': b[0],
                            'Sec-Fetch-Site': 'same-origin'
                        }

                        ds = urllib.urlencode({
                            'url_noticia': page_url,
                            'submit_enviar_url': 'ok',
                            'current_url': b[0]
                        })
                        
                        request = urllib2.Request("https://eljaviero.com/descargarvideosdelatele/index.php", data=ds, headers=hs)
                        data = json.loads(urllib2.urlopen(request, timeout = 60).read())

                        if 'prueba de nuevo' in data['mensaje']:
                            repeat = repeat + 1
                        else:
                            a = data['mensaje'].split('.m3u8')
                            b = a[0].split('>')
                            c = a[1].split('<')

                            u_f = b[-1] + '.m3u8' + c[0]
                            u_f2 = u_f.replace('/vcgdrm/', '/vcg/')

                            dbcur.execute("INSERT INTO links VALUES ('" + page_url + "', '" + u_f2 + "');")
                            dbcon.commit()

                            return u_f2
                    else:

                        dbcur.execute("INSERT INTO links VALUES ('" + page_url + "', '" + final_url + "');")
                        dbcon.commit()
                        
                        return final_url

                if repeat > 0:
                    xbmc.sleep(random.randint(100,650))
                    return get_video_url(page_url, repeat)

mode = args.get('mode', None)

if mode is None:

    request = urllib2.Request('https://www.atresplayer.com/')
    index_html = urllib2.urlopen(request).read()

    sections = []

    a = index_html.split('SiteNavigationElement","name":"')

    for x in range(1, len(a)):
        b = a[x].split('"')
        c = a[x].split(',"url":"')
        d = c[1].split('"')
        sections.append({'name': utf8me(b[0]), 'url': d[0].replace('\\u002F', '/')})

    for item in sections:
        url = build_url({'mode': 'indice', 'title': item['name'], 'href': item['url']})
        li = xbmcgui.ListItem(item['name'], iconImage = PATH + '/icon.png')
        li.setInfo(type="Video", infoLabels={"plot": item['name']})
        li.setArt({'fanart': PATH + '/fanart.jpg'})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'indice':

    request = urllib2.Request(args['href'][0])
    cat_html = urllib2.urlopen(request).read()

    a = cat_html.split('"redirect":false,"href":"')
    b = a[1].split('"')
    c = b[0].split('channel\u002F')
    d = c[1].split('?')
    cha_id = d[0]
    e = b[0].split('categoryId=')
    cat_id = e[1]

    request = urllib2.Request('https://api.atresplayer.com/client/v1/row/search?entityType=ATPFormat&sectionCategory=true&mainChannelId=' + cha_id + '&categoryId=' + cat_id + '&sortType=AZ&size=100&page=0')
    cat_json = json.loads(urllib2.urlopen(request).read())

    shows = []

    for item in cat_json['itemRows']:
        shows.append({
            "id" : item['formatId'],
            "title" : utf8me(item['title']),
            "image" : item['image']['pathHorizontal'],
            "href" : utf8me(item['link']['url']),
            "legal_title" : only_legal_chars(item['title']).lower()
        })

    total_pages = int(cat_json['pageInfo']['totalPages'])

    if total_pages > 0:
        for x in range(1, total_pages):
            request = urllib2.Request('https://api.atresplayer.com/client/v1/row/search?entityType=ATPFormat&sectionCategory=true&mainChannelId=' + cha_id + '&categoryId=' + cat_id + '&sortType=AZ&size=100&page=' + str(x))
            cat_json = json.loads(urllib2.urlopen(request).read())
            for item in cat_json['itemRows']:
                shows.append({
                    "id" : item['formatId'],
                    "title" : utf8me(item['title']),
                    "image" : item['image']['pathHorizontal'],
                    "href" : utf8me(item['link']['url']),
                    "legal_title" : only_legal_chars(item['title']).lower()
                })

    shows = sorted(shows, key = lambda i: i['legal_title'],reverse=False)

    for item in shows:
        url = build_url({'mode': 'show', 'title': item['title'], 'href': item['href'], 'id': item['id']})
        li = xbmcgui.ListItem(item['title'], iconImage = item['image'])
        li.setInfo(type="Video", infoLabels={"plot": item['title']})
        li.setArt({'fanart': item['image']})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'show':

    request = urllib2.Request('https://api.atresplayer.com/client/v1/row/search?entityType=ATPEpisode&formatId=' + args['id'][0] + '&size=100&page=0')
    show_data = urllib2.urlopen(request).read()
    show_json = json.loads(show_data)

    episodes = []

    if 'itemRows' in show_json:

        for item in show_json['itemRows']:
            tag = ''
            if 'tagType' in item:
                tag = '[P]'
            episodes.append({
                "title" : utf8me(item['title']),
                "subtitle" : utf8me(item['subTitle']),
                "image" : item['image']['pathHorizontal'],
                "href" : utf8me(item['link']['url']),
                "type" : tag
            })

        total_pages = int(show_json['pageInfo']['totalPages'])

        if total_pages > 0:
            for x in range(1, total_pages):
                request = urllib2.Request('https://api.atresplayer.com/client/v1/row/search?entityType=ATPEpisode&formatId=' + args['id'][0] + '&size=100&page=' + str(x))
                show_json = json.loads(urllib2.urlopen(request).read())
                for item in show_json['itemRows']:
                    tag = ''
                    if 'tagType' in item:
                        tag = '[P]'
                    episodes.append({
                        "title" : utf8me(item['title']),
                        "subtitle" : utf8me(item['subTitle']),
                        "image" : item['image']['pathHorizontal'],
                        "href" : utf8me(item['link']['url']),
                        "type" : tag
                    })

        for item in episodes:
            url = build_url({'mode': 'episode', 'title': item['title'], 'href': item['href'], 'image': item['image']})
            li = xbmcgui.ListItem(item['title'], iconImage = item['image'])
            li.setInfo(type="Video", infoLabels={"plot": item['title']})
            li.setArt({'fanart': item['image']})
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

        xbmcplugin.endOfDirectory(addon_handle)

    else:

        xbmc.executebuiltin('XBMC.Notification(%s, %s, %s, %s)' % ('No hay videos', 'No se han encontrado videos para este programa', 4000, PATH + '/icon.png'))

elif mode[0] == 'episode':

    video = get_video_url('https://www.atresplayer.com' + args['href'][0], 0)

    if video == '':

        xbmc.executebuiltin('XBMC.Notification(%s, %s, %s, %s)' % ('Video no accesible', "Puede que sea muy nuevo o que aun no se haya emitido. Prueba mas adelante.", 15000, PATH + '/icon.png'))

    else:

        m3u8_data = requests.get(video).text

        if '.m3u8' in video:
            listitem = xbmcgui.ListItem(args['title'][0])
            listitem.setInfo('video', {'Title': args['title'][0]})
            xbmc.Player().play(video, listitem)
        else:
            options = []
            player = f4mProxyHelper()
            
            url_to_play, item = player.playF4mLink(video, args['title'][0], None, True, 0, False, '', 'HDS', True, None, '', '', args['image'][0])
            item.setProperty("IsPlayable", "true")
            b = m3u8_data.split('bitrate="')
            titulo = item.getLabel().decode('utf8')

            for i in range(1, len(b)):
                c = b[i].split('"')
                options.append({'q': int(c[0])})

            options = sorted(options, key = lambda i: i['q'],reverse=True)

            for option in options:
                item.setLabel('[B]' + titulo + '[/B] | ' + str(option['q']) + ' kbps')
                item.setInfo(type="Video", infoLabels={"plot": args['title'][0]})
                item.setArt({'fanart': args['image'][0]})
                item.setProperty("IsPlayable","true")
                xbmcplugin.addDirectoryItem(handle=addon_handle, url=url_to_play.replace('maxbitrate=0', 'maxbitrate=' + str(option['q'])), listitem=item, isFolder=False)
            xbmcplugin.endOfDirectory(addon_handle)