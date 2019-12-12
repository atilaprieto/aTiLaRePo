# -*- coding: utf-8 -*-

from libs.tools import *
from libs import jsunpack
import threading


def list_all_channels(item):
    itemlist = list()
    canales =list()

    canales.extend(get_channels_dailysport(item))
    canales.extend(get_channels_sporttv(item))

    for n, url_idioma in enumerate(canales):
        label = '[COLOR red]Canal %s[/COLOR]' % (n + 1)

        itemlist.append(item.clone(
            label = (label + ' (%s)' % url_idioma[1]) if url_idioma[1] else label,
            title = 'Canales [COLOR red]24[/COLOR] - Canal %s' % (n+1),
            action='play',
            isPlayable=True,
            url=url_idioma[0]
        ))

    return itemlist


def get_channels_dailysport(item):
    threads = list()
    ret = []

    def get_online(canal, ret):
        data = httptools.downloadpage(canal[1]).data
        url = re.findall(".*?source:\s*'(.*?)'", data)
        if url and httptools.downloadpage(url[-1], headers={'Referer': canal[1]}).code == 200:
            ret.append(canal)

    try:
        data = httptools.downloadpage('https://dailysport.pw').data
        idiomas = set(re.findall('Channel (\d+)\s([^<\(]+)', data))
        idiomas = dict(eval(str(idiomas).replace('Spanish', 'Español').replace('English','Ingles')))
    except:
        idiomas = dict()

    for n in range(1,11):
        url = 'https://dailysport.pw/c%s.php' % n
        t = threading.Thread(target=get_online, args=((n,url), ret))
        threads.append(t)
        t.setDaemon(True)
        t.start()

    running = [t for t in threads if t.isAlive()]
    while running:
        time.sleep(0.5)
        running = [t for t in threads if t.isAlive()]

    return [(x[1],idiomas.get(str(x[0]),'').strip()) for x in sorted(ret, key=lambda x: x[0])]


def play__dailysport(item):
    url = None
    header = 'User-Agent=%s&Referer=%s' % (urllib.quote(httptools.default_headers["User-Agent"]),
                                           item.url)

    try:
        data = httptools.downloadpage(item.url).data
        url = re.findall(".*?source:\s*'(.*?)'", data)[-1]
        url = url + '|' + header

        return {'action': 'play',
                'VideoPlayer': 'inputstream',
                'manifest_type': 'hls',
                'mimetype': 'application/vnd.apple.mpegurl',
                'license_key': '|' + header,
                'headers': header,
                'url': url,
                'titulo': item.title}

    except:
        pass

    xbmcgui.Dialog().ok('1x2',
                        'Ups!  Parece que en estos momentos no hay nada que ver en este enlace.',
                        'Intentelo mas tarde o pruebe en otro enlace, por favor.')
    return None


def get_channels_sporttv(item):
    a = [('https://sportzonline.co/channels/bra/br%s.php' %n, 'Portugues') for n in range(1, 4)]
    a.extend([('https://v2.sportzonline.to/channels/pt/sporttv%s.php' %n, 'Portugues') for n in range(1, 6)])
    return a


def play_sporttv(item):
    try:
        data = httptools.downloadpage(item.url).data
        url = 'https:' + re.findall('<iframe src="([^"]+)', data)[0]
        data = httptools.downloadpage(url, headers={'Referer': url}).data
        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

        packed = re.findall('<script>(eval.*?)</script>', data)[0]
        url = re.findall('source:"([^"]+)',  jsunpack.unpack(packed))

        ret = {'action': 'play', 'url': url[0], 'VideoPlayer': 'f4mtester', 'titulo': item.title}
        '''headers = 'User-Agent={0}&Referer={1}'.format(
            urllib.quote(httptools.default_headers["User-Agent"]), item.url)

        ret =  {'action': 'play',
                'VideoPlayer': 'inputstream',
                'manifest_type': 'hls',
                'mimetype': 'application/vnd.apple.mpegurl',
                'license_key': '|' + headers,
                'headers': headers,
                'url': url[0],# + '|' + headers,
                'titulo': item.title}'''

        return ret

    except:
        pass

    xbmcgui.Dialog().ok('1x2',
                        'Ups!  Parece que en estos momentos no hay nada que ver en este enlace.',
                        'Intentelo mas tarde o pruebe en otro enlace, por favor.')
    return None


def play(item):
    if 'dailysport.pw' in item.url:
        return play__dailysport(item)

    elif 'sportzonline' in item.url:
        return play_sporttv(item)
