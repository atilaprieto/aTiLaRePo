# -*- coding: utf-8 -*-

from libs.tools import *
from libs import jsunpack
import threading


def list_all_channels(item):
    itemlist = list()
    canales =list()

    canales.extend(get_channels_dailysport(item))
    canales.extend(get_channels_sporttv(item))

    for n_url_idioma in canales:
        n, url, idioma = n_url_idioma

        label = '[COLOR red]Canal %s[/COLOR]' % n

        itemlist.append(item.clone(
            label=(label + ' (%s)' % idioma) if idioma else label,
            title='Canales [COLOR red]24[/COLOR] - Canal %s' % n,
            action='play',
            isPlayable= True,
            url=url
        ))

    return itemlist


def get_channels_dailysport(item):
    threads = list()
    ret = []

    def get_online(canal, ret):
        data = httptools.downloadpage(canal[1],timeout=1)
        url = re.findall("source:\s*'([^']+)'", data.data)
        if url:
            res= httptools.downloadpage(url[-1], headers={'Referer': canal[1]})
            if res.headers:
                #logger("%s - %s" % (canal[0], res.headers))
                last_modified = datetime.datetime.strptime(res.headers['last-modified'][5:-4], '%d %b %Y %H:%M:%S')
                date = datetime.datetime.strptime(res.headers['date'][5:-4], '%d %b %Y %H:%M:%S')
                if last_modified > date - datetime.timedelta(minutes=15):
                    ret.append(canal)

    try:
        data = httptools.downloadpage('https://dailysport.pw').data
        idiomas = set(re.findall('Channel (\d+)\s([^<(]+)', data))
        idiomas = dict(eval(str(idiomas).replace('Spanish', 'Español').replace('English','Ingles')))
    except:
        idiomas = dict()

    for n in range(1,11):
        url = 'https://dailysport.pw/c%s.php' % n
        t = threading.Thread(target=get_online, args=((n,url), ret))
        threads.append(t)
        t.setDaemon(True)
        t.start()
        
    to = 0
    #logger(to)
    running = [t for t in threads if t.isAlive()]
    while running and to < 10.5:
        time.sleep(0.5)
        to += 0.5
        running = [t for t in threads if t.isAlive()]
    #logger(to)

    return [(x[0],x[1],idiomas.get(str(x[0]),'').strip()) for x in sorted(ret, key=lambda x: x[0])]


def play__dailysport(item):
    url = None
    header = 'User-Agent=%s&Referer=%s' % (urllib.quote(httptools.default_headers["User-Agent"]),
                                           item.url)

    try:
        data = httptools.downloadpage(item.url).data
        url = re.findall("source:\s*'([^']+)'", data)[-1]
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
    a = [(n + 19, 'https://sportzonline.co/channels/bra/br%s.php' %n, 'Portugues') for n in range(1, 4)]
    a.extend([(n + 22, 'https://v2.sportzonline.to/channels/pt/sporttv%s.php' % n, 'Portugues') for n in range(1, 6)])
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
