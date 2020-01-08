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
import unicodedata
import re
from lib import youtube_dl
from types import UnicodeType
 
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
my_addon = xbmcaddon.Addon()
PATH = my_addon.getAddonInfo('path')
sys.path.append(xbmc.translatePath(os.path.join(PATH, 'lib')))

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

def get_video_url(page_url):
    video_urls = []
    
    ydl = youtube_dl.YoutubeDL({'outtmpl': u'%(id)s%(ext)s'})
    result = ydl.extract_info(page_url, download=False)

    for entries in result["formats"]:

        if entries["ext"] != "rtmp":
            video_url = safe_unicode(entries['url']).encode('utf-8')
            video_url = video_url.replace("http://ignore.mediaset.es", "http://miteleooyala-a.akamaihd.net")

            if entries["ext"] != "mp4":
                title = safe_unicode(entries["format"]).encode('utf-8')

            elif entries["ext"] == "mp4":

                if entries.has_key("vbr"):
                    title = "mp4-" + safe_unicode(str(entries["vbr"])).encode('utf-8') + " " + safe_unicode(entries["format"]).encode('utf-8').rsplit("-",1)[1]
                else:
                    title = safe_unicode(entries["format"]).encode('utf-8')

            try:
                calidad = int(safe_unicode(str(entries["vbr"])))
            except:
                try:
                    calidad = int(title.split("-")[1].strip())
                except:
                    calidad = 3000

            video_urls.append(["%s" % title, video_url, 0, False, calidad])
            
    video_urls.sort(key=lambda video_urls: video_urls[4], reverse=True)

    return video_urls

def get_json(html_in):
    a = html_in.split('window.$REACTBASE_STATE.navigation_mtweb = ')
    b = a[1].split(' </script>')
    return b[0]

def encodeit(string_in):
    return string_in.replace('/', '%252F').replace('-', '%252D')

mode = args.get('mode', None)

if mode is None:

    accept_sections = {
        '/programas-tv/',
        '/series-online/',
        '/deportes/',
        '/tv-movies/',
        '/miniseries/',
        '/peliculas/',
        '/documentales/',
        '/informativos/',
        '/musica/'
    }

    direct_sections = {
        '/tv-movies/',
        '/documentales/',
        '/peliculas/'
    }

    hs = {
        'authority': 'www.mitele.es',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'sec-fetch-site': 'none',
        'accept-language': 'es-ES,es;q=0.9'
    }

    request = urllib2.Request('https://www.mitele.es/', headers=hs)
    index_data = get_json(urllib2.urlopen(request).read())
    indice = json.loads(index_data)

    i = 0

    for item in indice['navigation']['section']['sections']:
        if i == 0:
            i = i + 1
        else:
            if item['link']['href'] in accept_sections:
                if item['link']['href'] in direct_sections:
                    url = build_url({'mode': 'indice', 'title': utf8me(item['title']), 'href': item['link']['href'], 'direct': '1'})
                else:
                    url = build_url({'mode': 'indice', 'title': utf8me(item['title']), 'href': item['link']['href'], 'direct': '0'})
                li = xbmcgui.ListItem(utf8me(item['title']), iconImage = PATH + '/icon.png')
                li.setInfo(type="Video", infoLabels={"plot": utf8me(item['title'])})
                li.setArt({'fanart': PATH + '/fanart.jpg'})
                xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'indice':

    hs = {
        'authority': 'mab.mediaset.es',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'sec-fetch-site': 'none',
        'accept-language': 'es-ES,es;q=0.9'
    }

    request = urllib2.Request('https://mab.mediaset.es/1.0.0/get?oid=bitban&eid=%2FautomaticIndex%2Fmtweb%3Furl%3Dwww%252Emitele%252Ees%252F' + args['href'][0].replace('/','') + '%252F%26page%3D1%26id%3Da-z%26size%3D50', headers=hs)
    
    indice = json.loads(urllib2.urlopen(request).read())

    shows = []

    for item in indice['editorialObjects']:
        shows.append({
            "id" : item['id'],
            "title" : item['title'],
            "image" : item['image']['src'],
            "href" : item['image']['href'],
            "legal_title" : only_legal_chars(item['title']).lower()
        })

    total_pages = int(indice['pagination']['totalPages'])

    if total_pages > 1:
        for x in range(2, total_pages + 1):
            request = urllib2.Request('https://mab.mediaset.es/1.0.0/get?oid=bitban&eid=%2FautomaticIndex%2Fmtweb%3Furl%3Dwww%252Emitele%252Ees%252F' + args['href'][0].replace('/','') + '%252F%26page%3D' + str(x) + '%26id%3Da-z%26size%3D50', headers=hs)
            indice = json.loads(urllib2.urlopen(request).read())
            for item in indice['editorialObjects']:
                shows.append({
                    "id" : item['id'],
                    "title" : item['title'],
                    "image" : item['image']['src'],
                    "href" : item['image']['href'],
                    "legal_title" : only_legal_chars(item['title']).lower()
                })

    shows = sorted(shows, key = lambda i: i['legal_title'],reverse=False)

    for item in shows:
        if args['direct'][0] == '0':
            url = build_url({'mode': 'show', 'title': utf8me(item['title']), 'href': item['href']})
        else:
            url = build_url({'mode': 'episode', 'title': utf8me(item['title']), 'href': item['href'] + 'player/'})
        li = xbmcgui.ListItem(utf8me(item['title']), iconImage = item['image'])
        li.setInfo(type="Video", infoLabels={"plot": utf8me(item['title'])})
        li.setArt({'fanart': item['image']})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'show':

    tabs = []

    hs = {
        'authority': 'www.mitele.es',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'sec-fetch-site': 'none',
        'accept-language': 'es-ES,es;q=0.9'
    }

    request = urllib2.Request('https://www.mitele.es' + args['href'][0], headers=hs)
    html_show = urllib2.urlopen(request).read()

    a = html_show.split('window.$REACTBASE_STATE.container_mtweb = ')

    b = a[1].split('</script>')

    json_data = json.loads(b[0].strip())

    for x in range(0, len(json_data['container']['tabs'])):

        tabs.append({
            'id': json_data['container']['tabs'][x]['id'], 
            'name': json_data['container']['tabs'][x]['title'], 
            'link': json_data['container']['tabs'][x]['link']['href']
        })

    episodes_list = []

    hs2 = {
        'authority': 'mab.mediaset.es',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'sec-fetch-site': 'none',
        'accept-language': 'es-ES,es;q=0.9'
    }

    for x in range(0, len(tabs)):

        if tabs[x]['name'] != 'Detalles':

            request = urllib2.Request('https://mab.mediaset.es/1.0.0/get?oid=bitban&eid=%2Ftabs%2Fmtweb%3Furl%3Dwww%252Emitele%252Ees' + encodeit(tabs[x]['link']) + '%26tabId%3D' + tabs[x]['id'], headers=hs2)
            json_data = urllib2.urlopen(request).read()
            json_show = json.loads(json_data)

            if json_show['type'] == 'navigation':

                for y in range(0, len(json_show['contents'])):

                    request2 = urllib2.Request('https://mab.mediaset.es/1.0.0/get?oid=bitban&eid=%2Ftabs%2Fmtweb%3Furl%3Dwww%252Emitele%252Ees' + encodeit(json_show['contents'][y]['link']['href']) + '%26tabId%3D' + tabs[x]['id'], headers=hs2)
                    json_data2 = urllib2.urlopen(request2).read()
                    json_show2 = json.loads(json_data2)

                    for s in range(0, len(json_show2['contents'])):

                        if 'children' in json_show2['contents'][s]:

                            paginas = json_show2['contents'][s]['pagination']['totalPages']

                            for t in range(1, int(paginas)+1):
                                if t == 1:

                                    for c in range(0, len(json_show2['contents'][s]['children'])):
                                        if 'title' in json_show2['contents'][s]['children'][c]:
                                            title = json_show2['contents'][s]['children'][c]['title']
                                            if 'subtitle' in json_show2['contents'][s]['children'][c]:
                                                subtitle = json_show2['contents'][s]['children'][c]['subtitle']
                                            else:
                                                subtitle = ''
                                            image = json_show2['contents'][s]['children'][c]['images']['thumbnail']['src']
                                            href = json_show2['contents'][s]['children'][c]['link']['href']
                                            duration = json_show2['contents'][s]['children'][c]['info']['duration']
                                            episode_n = json_show2['contents'][s]['children'][c]['info']['episode_number']

                                            episodes_list.append({
                                                'tab': tabs[x]['name'],
                                                'title' : title,
                                                'subtitle' : subtitle,
                                                'image' : image,
                                                'href' : href,
                                                'duration' : duration,
                                                'episode_n' : episode_n
                                            })

                                else:
                                    request2 = urllib2.Request('https://mab.mediaset.es/1.0.0/get?oid=bitban&eid=%2Ftabs%2Fmtweb%3Furl%3Dwww%252Emitele%252Ees' + encodeit(json_show['contents'][y]['link']['href']) + '%26tabId%3D' + tabs[x]['id'] + '%26size%3D50%26page%3D' + str(t), headers=hs2)
                                    json_data2 = urllib2.urlopen(request2).read()
                                    json_show2 = json.loads(json_data2)

                                    for s in range(0, len(json_show2['contents'])):

                                        if 'children' in json_show2['contents'][s]:
                                            for c in range(0, len(json_show2['contents'][s]['children'])):
                                                if 'title' in json_show2['contents'][s]['children'][c]:
                                                    title = json_show2['contents'][s]['children'][c]['title']
                                                    if 'subtitle' in json_show2['contents'][s]['children'][c]:
                                                        subtitle = json_show2['contents'][s]['children'][c]['subtitle']
                                                    else:
                                                        subtitle = ''
                                                    image = json_show2['contents'][s]['children'][c]['images']['thumbnail']['src']
                                                    href = json_show2['contents'][s]['children'][c]['link']['href']
                                                    duration = json_show2['contents'][s]['children'][c]['info']['duration']
                                                    episode_n = json_show2['contents'][s]['children'][c]['info']['episode_number']

                                                    episodes_list.append({
                                                        'tab': tabs[x]['name'],
                                                        'title' : title,
                                                        'subtitle' : subtitle,
                                                        'image' : image,
                                                        'href' : href,
                                                        'duration' : duration,
                                                        'episode_n' : episode_n
                                                    })



            else:

                for c in range(0, len(json_show['contents'])):
                    if 'title' in json_show['contents'][c]:
                        title = json_show['contents'][c]['title']
                        subtitle = json_show['contents'][c]['subtitle']
                        image = json_show['contents'][c]['images']['thumbnail']['src']
                        href = json_show['contents'][c]['link']['href']
                        duration = json_show['contents'][c]['info']['duration']
                        episode_n = json_show['contents'][c]['info']['episode_number']

                        episodes_list.append({
                            'tab': tabs[x]['name'],
                            'title' : title,
                            'subtitle' : subtitle,
                            'image' : image,
                            'href' : href,
                            'duration' : duration,
                            'episode_n' : episode_n
                        })

    for item in episodes_list:

        url = build_url({'mode': 'episode', 'title': utf8me(item['title']), 'href': item['href']})
        li = xbmcgui.ListItem(utf8me(item['tab']) + ' - ' + utf8me(item['title']), iconImage = item['image'])
        li.setInfo(type="Video", infoLabels = {
            "plot": "[B]" + args['title'][0] + "\n\n[/B]" + utf8me(item['tab']) + ' - ' + utf8me(item['title']) + "\n\n" + utf8me(item['subtitle']), 
            "Title" : utf8me(item['title']), 
            "Duration" : item['duration']
        })
        li.setArt({'fanart': item['image']})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'episode':

    videos = get_video_url('https://www.mitele.es' + args['href'][0].replace('/player/player', '/player'))
    listitem = xbmcgui.ListItem(args['title'][0])
    listitem.setInfo('video', {'Title': args['title'][0]})
    xbmc.Player().play(videos[0][1], listitem)