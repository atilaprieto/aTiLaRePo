# -*- coding: utf-8 -*-

from libs.tools import *
import threading

HOST = "http://www.720pstream.me"


def mainmenu(item):
    itemlist = list()

    itemlist.append(item.clone(
        label='MLB',
        action='get_eventos',
        url= HOST + '/live-mlb-stream',
        icon=os.path.join(image_path, 'mlb.png')
    ))

    itemlist.append(item.clone(
        label='NBA',
        action='get_eventos',
        url=HOST + '/live-nba-stream',
        icon=os.path.join(image_path, 'nba.png')
    ))

    itemlist.append(item.clone(
        label='NFL',
        action='get_eventos',
        url=HOST + '/nfl-stream',
        icon=os.path.join(image_path, 'nfl.png')
    ))

    itemlist.append(item.clone(
        label='NHL',
        action='get_eventos',
        url=HOST + '/nhl-stream',
        icon=os.path.join(image_path, 'nhl.png')
    ))

    itemlist.append(item.clone(
        label='UFC',
        action='get_eventos',
        url=HOST + '/mma-stream',
        icon=os.path.join(image_path, 'ufc.png'),
    ))

    itemlist.append(item.clone(
        label='NCAAF',
        action='get_eventos',
        url=HOST + '/ncaaf-stream',
        icon=os.path.join(image_path, 'ncaaf.png'),
    ))

    itemlist.append(item.clone(
        label='NCAAM',
        action='get_eventos',
        url=HOST + '/ncaam-stream',
        icon=os.path.join(image_path, 'ncaam.png'),
    ))

    return itemlist


def get_eventos(item):
    itemlist = list()
    fechas = []
    threads = list()
    ret = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}", "", data)

    patron = '<div class="card card-body border-secondary mb-3"><a title="([^"]+)" href="([^"]+)".*?text-warning">(.*?)</div>(.*?)</div></div></a></div>'
    eventos = re.findall(patron,data)

    for ev in eventos[:]:
        if 'Watch Now' in ev[3]:
            eventos.remove(ev)
            t = threading.Thread(target=check_event, args=(ev, ret))
            threads.append(t)
            t.setDaemon(True)
            t.start()

    running = [t for t in threads if t.isAlive()]
    while running:
        time.sleep(0.5)
        running = [t for t in threads if t.isAlive()]

    if ret:
        itemlist.append(item.clone(
            label='[B][COLOR green]Ver Ahora:[/COLOR][/B]',
            icon=os.path.join(image_path, '720pstream.png'),
            action=None
        ))

        for titulo, url, tiempo, back in ret:
            titulo = titulo.replace(' Live Stream', '').replace('@', ' vs. ',1)
            itemlist.append(item.clone(
                label='[B][COLOR green]     %s[/COLOR][/B]' % titulo,
                title=titulo,
                action='play',
                isPlayable=True,
                url=HOST + url
            ))


    for titulo, url, tiempo, back in eventos:
        titulo = titulo.replace(' Live Stream', '').replace('@', ' vs. ',1)
        tiempo = re.findall("<time datetime='([^']+)'>", tiempo)[0]
        utc_datetime = datetime.datetime.strptime(tiempo, "%Y-%m-%dT%H:%M")
        fecha_hora_local = datetime_to_local(utc_datetime, 'UTC', +5)
        fecha = fecha_hora_local.date().strftime('%d/%m/%Y')

        if not fecha in fechas:
            fechas.append(fecha)
            itemlist.append(item.clone(
                label='[B][COLOR gold]%s[/COLOR][/B]' % fecha,
                icon=os.path.join(image_path, '720pstream.png'),
                action=None
            ))

        hora = fecha_hora_local.time().strftime('%H:%M')

        itemlist.append(item.clone(
            label="%s %s" %(hora, titulo),
            title=titulo,
            action='play',
            isPlayable=True,
            url=HOST + url
        ))

    if not itemlist:
        xbmcgui.Dialog().ok('1x2',
                            'Ups!  Parece que en estos momentos no hay eventos programados.',
                            'Intentelo mas tarde, por favor.')
    return itemlist


def check_event(evento, ret):
    data = httptools.downloadpage(HOST + evento[1]).data

    if 'videoURI' in data:
        url = re.findall("videoURI = '([^']+)", data)[0]
        data = httptools.downloadpage(url).data
        if data.startswith("#EXTM3U"):
            ret.append(evento)

    elif "embed-responsive-item" in data:
        url = re.findall("""class=["|']embed-responsive-item["|'] src='([^']+)""", data)
        if url:
            data = httptools.downloadpage(url[0]).data
            if not 'Event Completed' in data:
                ret.append(evento)


def f4mcallback(param, tipo, error, Cookie_Jar, url, headers):
    logger("####################### f4mcallback ########################")
    param = eval(param)
    data = httptools.downloadpage(param[0]).data
    urlnew = re.findall("videoURI = '([^']+)", data)[0]

    return urlnew, Cookie_Jar


def play(item):
    data = httptools.downloadpage(item.url).data

    if 'videoURI' in data:
        logger("play VideoURI")
        url = re.findall("videoURI = '([^']+)", data)[0]
        headers = 'User-Agent={0}&Referer={1}&Origin=http://www.720pstream.me'.format(
            urllib.quote(httptools.default_headers["User-Agent"]), item.url)

        return {'action': 'play',
                'VideoPlayer': 'inputstream',
                'manifest_type': 'hls',
                'mimetype': 'application/vnd.apple.mpegurl',
                'license_key': '|' + headers,
                'headers': headers,
                'url': url,
                'titulo': item.title}

    elif "embed-responsive-item" in data:
        logger("play embed")
        try:
            url = re.findall("""class=["|']embed-responsive-item["|'] src='([^']+)""", data)[0]
            data = httptools.downloadpage(url).data

            pdettxt, zmid, pid, edm = re.findall('pdettxt\s?=\s?"([^"]+).*?zmid\s?=\s?"([^"]+).*?pid\s?=\s?(\d+).*?edm\s?=\s?"([^"]+)"', data)[0]
            url_embed = "https://" + edm + "/sdembed?v=" + zmid

            data = httptools.downloadpage(url_embed, post={'pid': pid,'ptxt': pdettxt}, headers={'referer': url}).data
            var = re.findall('stream=(\w+).*?"scode": "([^"]+)", "ts": (\d+)', data)[0]
            
            s = re.findall("\); } } (.*?'function '+.*?;)", data, re.S)[0]
            literales = re.findall("'(.*?)'",s)
            for n, l in enumerate(literales):
                if l == '': continue
                s = s.replace(l, '_%s_' %n)

            s = s.replace(',', '\n').replace(';', '\n')

            for n, l in enumerate(literales):
                if l == '': continue
                s = s.replace('_%s_' % n, l)

            exec (s)

            f = re.findall('(\w+)\s=', s)[-1]
            url = re.findall('"(http[^"]+)', eval(f))[0]

        except:
            logger("Error en play:\n%s" % data)

        else:
            thread = threading.Thread(name='authcheck', target=authcheck, args=[item.title, url_embed, var[0], var[1], var[2]])
            thread.setDaemon(True)
            thread.start()

            headers = 'User-Agent={0}&Referer={1}&Origin=https://www.kuntv.pw'.format(urllib.quote(httptools.default_headers["User-Agent"]), urllib.quote(url_embed))

            return {'action': 'play',
                    'VideoPlayer': 'inputstream',
                    'manifest_type': 'hls',
                    'license_key': '|' + headers,
                    'headers': headers,
                    'url': url,
                    'titulo': item.title}



    xbmcgui.Dialog().ok('1x2',
                        'Ups!  Parece que en estos momentos no hay nada que ver en este enlace.',
                        'Intentelo mas tarde o pruebe en otro enlace, por favor.')


def authcheck(title, referer, stream, code, exts):
    try:
        timeout = 0

        url_authme = 'https://authme.seckeyserv.me?stream=%s&scode=%s&expires=%s' % (stream, code, exts)
        ret = httptools.downloadpage(url_authme, headers={'referer': referer})

        if ret.code != 200:
            raise Exception("HTTP CODE %s" % ret.code)
        data = ret.data

        player = xbmc.Player()
        isPlaying = player.isPlaying()

        while not isPlaying and timeout < 30:
            xbmc.sleep(1000)
            timeout += 1
            isPlaying = player.isPlaying()

        if timeout == 30:
            raise Exception("Timeout")

        while player.isPlaying():
            player_title = ""
            timeout = 0
            while not player_title and timeout < 10:
                xbmc.sleep(1000)
                timeout += 1
                try:
                    player_title = xbmc.Player().getVideoInfoTag().getTitle()
                except:
                    pass

            if player_title != title:
                raise Exception("Timeout or no title")

            res = load_json(data)
            if res['success'] != "true":
                raise Exception("No Success")

            url_authme = 'https://authme.seckeyserv.me?stream=%s&scode=%s&exts=%s' % (stream, res['scode'], res['ts'])
            ret = httptools.downloadpage(url_authme, headers={'referer': referer})
            if ret.code != 200:
                raise Exception("HTTP CODE %s" % ret.code)
            data = ret.data
            logger("######################### authcheck ok #########################", 'info')
            xbmc.sleep(300000)

    except Exception as inst:
        logger("######################### authcheck fail #########################", 'info')
        logger(inst, 'info')
    else:
        logger("######################### authcheck end #########################", 'info')
