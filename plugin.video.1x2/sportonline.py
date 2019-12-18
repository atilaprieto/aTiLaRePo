# -*- coding: utf-8 -*-

from libs.tools import *
from libs import jsunpack
import threading

def mainmenu(item):
    itemlist = list()

    itemlist.append(item.clone(
        label='Agenda',
        action='get_agenda',
        #icon=os.path.join(image_path, 'arenavisionlogo1.png'),
        plot='Muestra la Agenda SportOnline'
    ))

    itemlist.append(item.clone(
        label='Canales',
        action='list_all_channels',
        # icon=os.path.join(image_path, 'arenavisionlogo1.png'),
        plot='Muestra todos los canales en directo'
    ))

    return itemlist


def list_all_channels(item):
    itemlist = list()

    for n, url in enumerate(get_channels_sportzonline()):
        itemlist.append(item.clone(
            label = '[COLOR red]Canal %s[/COLOR]' % (n + 1),
            title = 'SportOnline - Canal %s' % (n+1),
            action='play',
            isPlayable=True,
            url=url
        ))

    return itemlist


def get_channels_sportzonline():
    threads = list()
    ret = []

    def check_channel(url_ini, ret):
        data = httptools.downloadpage(url_ini).data
        url = 'https:' + re.findall('<iframe src="([^"]+)', data)[0]
        data = httptools.downloadpage(url, headers={'Referer': url}).data
        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

        packed = re.findall('<script>(eval.*?)</script>', data)[0]
        url = re.findall('source:"([^"]+)', jsunpack.unpack(packed))

        if url and httptools.downloadpage(url[0]).code == 200:
            ret.append(url_ini)

    for n in range(1, 9):
        url = 'https://sportzonline.co/channels/hd/hd%s.php' %n
        t = threading.Thread(target=check_channel, args=(url, ret))
        threads.append(t)
        t.setDaemon(True)
        t.start()

    running = [t for t in threads if t.isAlive()]
    while running:
        time.sleep(0.5)
        running = [t for t in threads if t.isAlive()]

    return ret



def read_guide():
    guide = list()
    idioma_esp = {
        'ITALIAN': 'Italiano',
        'ENGLISH': 'Inglés',
        'DUTCH': 'Holandes',
        'GERMAN': 'Alemán',
        'POLISH': 'Polaco',
        'FRENCH': 'Francés',
        'SPANISH': 'Español',
        'GREEK': 'Griego',
        'BRAZILIAN': 'Portugues',
        'ROMANIAN': 'Rumano',
        'TURKISH': 'Turco'}
    week = ['MONDAY','TUESDAY','WENSDAY','THURSDAY','FRIDAY','SATURDAY','SUNDAY']

    data = re.sub(r"\r", "", httptools.downloadpage('https://sportzonline.to/prog.txt').data)
    data = re.sub(r"(MONDAY|TUESDAY|WENSDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY)\n", r"%&%\1\n", data) + '\n%&%'
    #logger(data)

    # dia actualizacion
    fecha_up = re.findall('LAST UPDATE\s?:\s?(\d{1,2}-\d{1,2}-)', data)[0] + '2019'
    up_datetime = datetime.datetime.strptime(fecha_up, '%d-%m-%Y')
    #logger(week[up_datetime.weekday()])

    agenda = re.findall('(MONDAY|TUESDAY|WENSDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY)(.*?)%&%', data,re.MULTILINE|re.DOTALL)

    if agenda:
        c1 = week.index(agenda[0][0].upper()) + 1
        if c1 == 7: c1 = 0
        if up_datetime.weekday() == c1:
            up_datetime = up_datetime - datetime.timedelta(days=1)

    # agenda diaria
    for ad in agenda:
        #logger(week.index(ad[0].upper()))
        if up_datetime.weekday() < week.index(ad[0].upper()):
            fecha_evento = up_datetime + datetime.timedelta(days=week.index(ad[0].upper()) - up_datetime.weekday())
        elif up_datetime.weekday() > week.index(ad[0].upper()):
            fecha_evento = up_datetime + datetime.timedelta(days=week.index(ad[0].upper()) + 7 - up_datetime.weekday())
        else:
            fecha_evento = up_datetime
        #logger(fecha_evento)

        # idiomas del dia
        idiomas_eng = dict(re.findall('(HD\d+)\s([^\s]+)', ad[1]))

        # eventos del dia
        hora_ant = datetime.time(0,0)
        for e in re.findall('(\d{1,2}:\d{2}.*?php)', ad[1]):
            hora, titulo, url = re.findall('(\d+:\d+)\s*([^|]+)\|\s(.*?)\.php', e)[0]

            if 'pt/sporttv' in url or '/bra/br' in url:
                idioma = 'Portugués'
            else:
                idioma = url.split('/')[-1].upper()
                idioma = idioma_esp.get(idiomas_eng.get(idioma), idioma)

            hora_evento = datetime.datetime.strptime(hora, '%H:%M').time()
            if hora_evento < hora_ant:
                fecha_evento = fecha_evento + datetime.timedelta(days=1)
            hora_ant = hora_evento
            dt_evento = datetime.datetime.combine(fecha_evento, hora_evento)
            fecha_hora_CEST = dt_evento + datetime.timedelta(hours=1)
            fecha_hora_local = date_to_local(datetime.datetime.strftime(fecha_hora_CEST, '%d/%m/%Y'),
                                       datetime.datetime.strftime(fecha_hora_CEST, '%H:%M'), 'CEST')

            guide.append({
                'fecha': fecha_hora_local.date(),
                'hora': fecha_hora_local.time(),
                'title': titulo.strip().replace(' x ', ' vs. ').replace(' @ ', ' vs. '),
                'url': url + '.php',
                'idioma': idioma})

    return guide


def get_agenda(item):
    itemlist = []

    fechas = list()
    le = dict()
    for evento in read_guide():
        id = '%s-%s-%s' %(evento['fecha'], evento['hora'], evento['title'])
        if id not in le:
            evento['url'] = [evento['url']]
            evento['idioma'] = [evento['idioma']]
            le[id]= evento
        else:
            le[id]['url'].append(evento['url'])
            le[id]['idioma'].append(evento['idioma'])


    for evento in sorted(le.values(), key=lambda x: (x['fecha'], x['hora'])):
        if evento['fecha'] not in fechas:
            fechas.append(evento['fecha'])
            label = evento['fecha'].strftime('%d/%m/%Y')
            itemlist.append(item.clone(
                label='[B][COLOR gold]%s[/COLOR][/B]' % label,
                icon=os.path.join(image_path, 'logo.gif'),
                action=None
            ))

        idiomas = evento['idioma'][0] if len(evento['idioma']) == 1 else ', '.join(set(evento['idioma']))
        new_item = item.clone(
            label= '%s %s (%s)' %(evento['hora'].strftime('%H:%M'), evento['title'], idiomas),
            title= evento['title']
            )

        if len(evento['url']) == 1:
            new_item.isPlayable=True
            new_item.action= 'play'
            new_item.url= evento['url'][0]
        else:
            new_item.isPlayable = False
            new_item.action = 'list_channels_play'
            new_item.url = evento['url']
            new_item.idiomas = evento['idioma']

        itemlist.append(new_item)

    return itemlist


def list_channels_play(item):
    itemlist = []

    for n,url in enumerate(item.url):
        itemlist.append(item.clone(
            label = 'Canal %s (%s)' %((n+1), item.idiomas[n]),
            isPlayable = True,
            action = 'play',
            url = url
        ))

    return itemlist


def play(item):
    try:
        data = httptools.downloadpage(item.url).data
        url = 'https:' + re.findall('<iframe src="([^"]+)', data)[0]
        data = httptools.downloadpage(url, headers={'Referer': url}).data
        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

        packed = re.findall('<script>(eval.*?)</script>', data)[0]
        url = re.findall('source:"([^"]+)',  jsunpack.unpack(packed))

        ret = {'action': 'play',
               'url': url[0],
               'VideoPlayer': 'directo',
               'titulo': item.title}

        return ret

    except:
        pass

    xbmcgui.Dialog().ok('1x2',
                        'Ups!  Parece que en estos momentos no hay nada que ver en este enlace.',
                        'Intentelo mas tarde o pruebe en otro enlace, por favor.')
    return None
