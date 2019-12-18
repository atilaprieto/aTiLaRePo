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
import unicodedata
from HTMLParser import HTMLParser
from lib import youtube_dl
from types import UnicodeType
 
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
my_addon = xbmcaddon.Addon()
PATH = my_addon.getAddonInfo('path')

sys.path.append(xbmc.translatePath(os.path.join(PATH, 'lib')))

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

def download_video_url(page_url, local_path, title):
    videos = get_video_url(page_url)
    a = videos[0].split('/')
    a[-1] = ''
    url_root = '/'.join(a)
    request = urllib2.Request(videos[0])
    response = urllib2.urlopen(request)
    line = response.readline().strip()
    CHUNK = 16 * 1024
    while line:
        if not line.startswith('#') and line != '':
            line_response = urllib2.urlopen(url_root + line)
            with open(local_path, 'ab') as f:
                while True:
                    chunk = line_response.read(CHUNK)
                    if not chunk:
                        break
                    f.write(chunk)
            f.close()
        line = response.readline().strip()
    xbmc.executebuiltin('XBMC.Notification(%s, %s, %s, %s)' % ('Descarga Finalizada', title, 4000, PATH + '/icon.png'))

def get_video_url(page_url):
    video_urls = []
    ydl = youtube_dl.YoutubeDL({'outtmpl': u'%(id)s%(ext)s'})
    result = ydl.extract_info(page_url, download=False)
    try:
        if "ext" in result and "url" in result:
            video_urls.append(safe_unicode(result['url']).encode('utf-8'))
        else:
            if "entries" in result:
                for entry in result["entries"]:
                    video_urls.append(safe_unicode(entry['url']).encode('utf-8'))
    except:
        import traceback
    return video_urls

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
    string_out = re.sub(r'[\\/:"*?<>|]+', "", string_out)
    string_out = "".join(i for i in string_out if ord(i)<128)
    string_out = ' '.join(string_out.split())
    return string_out

def get_last_page_episode(html_in):
    if '<a name="paginaIR" href="/alacarta/interno/contenttable.shtml?pbq=' in html_in:
        p = html_in.split('<a name="paginaIR" href="/alacarta/interno/contenttable.shtml?pbq=')
        q = p[len(p)-1].split('&')
        return q[0]
    else:
        return '1'

def split_and_get(html_in, text1, text2):
    a = html_in.split(text1)
    b = a[1].split(text2)
    return b[0]

def time_to_seconds(time_in):
    a = time_in.split(':')
    if len(a) > 1:
        if len(a) == 2:
            return (int(a[0])*60) + int(a[1])
        else:
            return (int(a[0])*60*60) + (int(a[1])*60) + int(a[2])
    else:
        return ''

def decode_html(value):
    try:
        unicode_title = unicode(value, "utf8", "ignore")
        return utf8me(HTMLParser().unescape(unicode_title).encode("utf8"))
    except:
        return utf8me(value)

mode = args.get('mode', None)

if mode is None:

    request = urllib2.Request('http://www.hirayasoftware.com/rtve_brain/index.json')
    index_data = urllib2.urlopen(request).read()
    indice = json.loads(index_data)

    for item in indice:
        url = build_url({'mode': 'indice', 'file': item['file']})
        li = xbmcgui.ListItem(utf8me(item['name']), iconImage = PATH + '/icon.png')
        li.setInfo(type="Video", infoLabels={"plot": utf8me(item['name'])})
        li.setArt({'fanart': PATH + '/fanart.jpg'})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'indice':

    request = urllib2.Request('http://www.hirayasoftware.com/rtve_brain/' + args['file'][0])
    shows_data = urllib2.urlopen(request).read()
    shows = json.loads(shows_data)

    for item in shows:
        url = build_url({'mode': 'show', 'id': item['id'], 'page': '1', 'name': decode_html(item['name']), 'logo': PATH + '/logos/' + item['logo'] + '.png'})
        li = xbmcgui.ListItem('[B]' + decode_html(item['name']) + '[/B]', iconImage = PATH + '/logos/' + item['logo'] + '.png')
        li.setInfo(type="Video", infoLabels={ "plot": "[B]" + decode_html(item['name']) + "[/B]\n\n" + utf8me(item['text']), "Title" : '[B]' + decode_html(item['name']) + '[/B]'})
        li.setArt({'fanart': PATH + '/fanart.jpg'})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'show':

    episodes = []

    request = urllib2.Request('http://www.rtve.es/alacarta/interno/contenttable.shtml?pbq=' + args['page'][0] + '&orderCriteria=DESC&modl=TOC&locale=es&pageSize=15&ctx=' + args['id'][0] + '&advSearchOpen=false')
    html_data = urllib2.urlopen(request).read()

    pieces = html_data.split('<span itemprop="name" content="')
    del pieces[0]
    for piece in pieces:
        a = piece.split('"></span>')

        episodes.append({
            'title': decode_html(a[0]),
            'id': split_and_get(piece, '<span class="col_tit" id="', '"'),
            'href': split_and_get(piece, '<a href="', '"'),
            'time': split_and_get(piece, '<span class="col_dur">', '</span>'),
            'text': decode_html(split_and_get(piece, '<span class="detalle">', '</span>'))
        })

    for episode in episodes:

        commands = []

        cmd = 'XBMC.RunPlugin({})'.format(build_url({'mode': 'download', 'title': args['name'][0] + ' - ' + episode['title'], 'href': episode['href']}))
        commands.append(( 'Descargar', cmd ))

        url = build_url({'mode': 'episode', 'title': episode['title'], 'href': episode['href']})
        li = xbmcgui.ListItem(episode['title'], iconImage = 'https://img2.rtve.es/v/' + episode['id'] + '/')
        li.setInfo(type="Video", infoLabels={ "plot": "[B]" + args['name'][0] + "\n\n[/B]" + episode['text'], "Title" : episode['title'], "Duration" : time_to_seconds(episode['time'])})
        li.setArt({'fanart': 'https://img2.rtve.es/v/' + episode['id'] + '/'})
        li.addContextMenuItems(commands)
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    episodes_pages = int(get_last_page_episode(html_data))

    if(int(args['page'][0]) < episodes_pages):
        url = build_url({'mode': 'show', 'id': args['id'][0], 'name': args['name'][0], 'logo': args['logo'][0], 'page': str(int(args['page'][0]) + 1)})
        li = xbmcgui.ListItem(utf8me('P\u00e1gina ') + str(int(args['page'][0]) + 1), iconImage = args['logo'][0])
        li.setInfo(type="Video", infoLabels={"plot": utf8me('P\u00e1gina ') + str(int(args['page'][0]) + 1)})
        li.setArt({'fanart': PATH + '/fanart.jpg'})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'episode':
    videos = get_video_url(args['href'][0])
    listitem = xbmcgui.ListItem(args['title'][0])
    listitem.setInfo('video', {'Title': args['title'][0]})
    xbmc.Player().play(videos[0], listitem)

elif mode[0] == 'download':
    dialog = xbmcgui.Dialog().browse(0, 'Elige un directorio para descargar el video', "video")
    if dialog != '':
        download_video_url(args['href'][0], dialog + only_legal_chars(args['title'][0]) + '.mp4', args['title'][0])