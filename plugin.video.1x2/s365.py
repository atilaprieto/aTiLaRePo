# -*- coding: utf-8 -*-

from libs.tools import *
import requests

HOST = get_setting('sport_url')


def mainmenu(item):
    itemlist = list()

    itemlist.append(item.clone(
        label='Agenda S365',
        channel='s365',
        action='get_agenda',
        icon=os.path.join(image_path, 'sport365_logo.png'),
        url=HOST + '/es/events/-/1/-/-/120',
        plot='Basada en la web %s' % HOST
    ))

    itemlist.append(item.clone(
        label='En Emisión',
        channel='s365',
        action='get_agenda',
        direct=True,
        icon=os.path.join(image_path, 'live.gif'),
        url=HOST + '/es/events/1/-/-/-/120',
        plot='Basada en la web %s' % HOST
    ))

    return itemlist


def read_guide(item):
    guide = []
    guide_agrupada = dict()

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    fechas = re.findall('<td colspan=9[^>]+>(\d+\.\d+\.\d+)<', data)

    for fecha in fechas:
        if fecha == fechas[-1]:
            bloque = re.findall('%s<(.*?)</table></div>' % fecha, data)[0]
        else:
            bloque = re.findall('%s<(.*?)%s' % (fecha, fechas[fechas.index(fecha) + 1]), data)[0]

        patron = 'onClick=.*?"event_([^"]+)".*?<td rowspan=2.*?src="([^"]+)".*?<td rowspan=2.*?>(\d+:\d+)<.*?<td.*?>' \
                 '([^<]+)<.*?<td.*?>(.*?)/td>.*?<tr.*?<td colspan=2.*?>([^<]+)</td><[^>]+>([^<]*)<'

        for code, thumb, hora, titulo, calidad, deporte_competicion, idioma in re.findall(patron, bloque):
            calidad = re.findall('>([\w\s?]+).*?</span>', calidad)
            if calidad:
                canales = [{'calidad': calidad[0].replace("HQ", "HD"),
                            'url': HOST + '/es/links/%s/1' % code,
                            'idioma': idioma}]
            else:
                canales = [{'calidad': 'N/A',
                            'idioma': idioma,
                            'url': HOST + '/es/links/%s/1' % code}]

            if ' / ' in deporte_competicion:
                deporte = deporte_competicion.split(' / ', 1)[0].strip()
                competicion = deporte_competicion.split(' / ', 1)[1].strip()
            else:
                deporte = deporte_competicion.strip()
                competicion = ''

            competicion = re.sub(r"World - ", "", competicion)
            if competicion.lower() in ['formula 1', 'moto gp']:
                deporte = competicion
                competicion = ''

            guide.append(Evento(fecha=fecha, hora=hora, formatTime='CEST', sport=deporte,
                                competition=competicion, title=titulo, channels=canales,
                                direct=True if "green-big.png" in thumb else False))

    for e in guide:
        key = "%s|%s" % (e.datetime, e.title)
        if key not in guide_agrupada:
            guide_agrupada[key] = e
        else:
            ev = guide_agrupada[key]
            ev.channels.extend(e.channels)

    return sorted(guide_agrupada.values(), key=lambda e: e.datetime)


def get_agenda(item, guide=None):
    itemlist = []

    if not guide:
        guide = read_guide(item)

    fechas = []
    for evento in guide:
        if item.direct and not evento.direct:
            continue

        if not item.direct and evento.fecha not in fechas:
            fechas.append(evento.fecha)
            label = '%s' % evento.fecha
            icon = os.path.join(image_path, 'logo.gif')

            itemlist.append(item.clone(
                label='[B][COLOR gold]%s[/COLOR][/B]' % label,
                icon=icon,
                action=None
            ))

        label = "[COLOR lime]" if evento.direct else "[COLOR red]"
        if evento.competition.label:
            label += "%s[/COLOR] (%s - %s)" % (evento.hora, evento.sport.label, evento.competition.label)
        else:
            label += "%s[/COLOR] (%s)" % (evento.hora, evento.sport.label)
        label = '%s %s' % (label, evento.title)

        new_item = item.clone(
            label=label,
            title=evento.title,
            icon=evento.get_icon())

        if not evento.direct:
            new_item.action = ""
        elif len(evento.channels) > 1:
            new_item.action = "ver_idiomas"
            new_item.channels = evento.channels
            new_item.label += ' [%s]' % evento.idiomas
        else:
            new_item.action = "get_enlaces"
            new_item.url = evento.channels[0]['url']
            new_item.label += ' [%s]' % evento.channels[0]['idioma']
            new_item.idioma = evento.channels[0]['idioma']
            new_item.calidad = evento.channels[0]['calidad']

        itemlist.append(new_item)

    if not itemlist:
        xbmcgui.Dialog().ok('1x2',
                            'Ups!  Parece que en estos momentos no hay eventos programados.',
                            'Intentelo mas tarde, por favor.')

    return itemlist


def ver_idiomas(item):
    itemlist = list()

    for i in item.channels:
        label = "   - %s" % i['idioma']
        if i['calidad'] != 'N/A':
            label += " (%s)" % i['calidad']

        itemlist.append(item.clone(
            label=label,
            action="get_enlaces",
            url=i['url'],
            idioma=i['idioma'],
            calidad=i['calidad']
        ))

    if itemlist:
        itemlist.insert(0, item.clone(action='', label='[B][COLOR gold]%s[/COLOR][/B]' % item.title))

    return itemlist


def get_enlaces(item):
    itemlist = list()

    data = httptools.downloadpage(item.url).data
    patron = "><span id='span_link_links.*?\('([^']+)"

    for n, data in enumerate(set(re.findall(patron, data))):
        url = decrypt(data)
        if url:
            itemlist.append(item.clone(
                label='    - Enlace %s' % (n + 1),
                action='play',
                url=url
            ))

    if itemlist:
        itemlist.insert(0, item.clone(
            action='',
            label='[B][COLOR gold]%s[/COLOR] [COLOR orange]%s (%s)[/COLOR][/B]' % (
                item.title, item.idioma, item.calidad)))

    return itemlist


def get_urlplay(url):
    try:
        s = requests.Session()
        header = {'User-Agent': httptools.default_headers["User-Agent"],
                  'Referer': url}

        content = s.get(url, headers=header).content
        url = re.findall('<iframe.*?src="([^"]+)', content)

        if url and not '/images/matras.jpg' in url[0]:
            link = re.sub(r'&#(\d+);', lambda x: chr(int(x.group(1))), url[0])
            data = s.get(link, headers=header).content

            post = {k: v for k, v in re.findall('<input type="hidden" name="([^"]+)" value="([^"]+)">', data)}
            action = re.findall("action', '([^']+)", data)
            data2 = httptools.downloadpage(action[0], post=post, headers=header).data
            data = re.findall("function\(\)\s*{\s*[a-z0-9]{43}\(.*?,.*?,\s*'([^']+)'", data2)[0]

            url = decrypt(data, re.findall('<script type="text/javascript" src="([^"]+)', data2))

            if not url: raise ()

            url_head = 'User-Agent=%s&Referer=%s' % (
                urllib.quote(httptools.default_headers["User-Agent"]), urllib.quote('http://h5.adshell.net/peer5'))

            return (url, url_head)
    except:
        logger("Error in get_url", 'error')
        return (None, None)


def decrypt(text, scripts=None):
    plaintext = ''
    exec("import base64\nfrom libs.tools import *\nif py_version.startswith('2.6'):\n\texec(base64.b64decode('aW1wb3J0I"
         "G1hcnNoYWwKZXhlYyhtYXJzaGFsLmxvYWRzKGJhc2U2NC5iNjRkZWNvZGUoIll3QUFBQUFBQUFBQUpBQUFBRUFBQUFCempBTUFBR1FBQUdRQk"
         "FHc0FBRm9BQUdRQUFHUUJBR3NCQUZvQkFHUUFBR1FCQUdzQ0FGb0NBR1FBQUdRQkFHc0RBRm9EQUdRQUFHUUNBR3NFQUd3RkFGb0ZBQUZrQXd"
         "DRUFBQmFCZ0JrQkFDRUFBQmFCd0JrQlFDRUFBQmFDQUJsQ1FCcENnQnBDd0JsQXdCcERBQmxBZ0JwRFFCa0JnQmtCd0JwRGdCa0NBQ0VBQUJr"
         "Q1FCa0NnQmtDd0JrREFCa0RRQmtEZ0JrRHdCa0VBQmtEUUJrRVFCa0VnQmtFd0JrRHdCa0ZBQmtGUUJrRmdCbkVBQkVnd0VBZ3dFQUZvTUJBR"
         "2tQQUdRWEFJTUJBSU1CQUlNQkFGb1FBR1VKQUdrS0FHa1JBR1VKQUdrS0FHa09BR1VRQUdRR0FHUUhBR2tPQUdRWUFJUUFBR1FKQUdRS0FHUU"
         "xBR1FNQUdRTkFHUU9BR1FQQUdRUUFHUU5BR1FSQUdRU0FHUVRBR1FQQUdRS0FHUU5BR1FRQUdRU0FHUVpBR1FRQUdRYUFHUVNBR1FiQUdRY0F"
         "HUU5BR1FkQUdjWkFFU0RBUUNEQVFBV2d3SUFnd0VBYnhFQUFXVUZBR1FlQUdRZkFJTUNBQUZ1SlFJQlpRSUFhUTBBZ3dBQWFROEFaQ0FBZ3dF"
         "QVpBWUFaQWNBYVE0QVpDRUFoQUFBWkFrQVpBb0FaQXNBWkF3QVpBMEFaQTRBWkE4QVpCQUFaQTBBWkJFQVpCSUFaQk1BWkE4QVpCUUFaQlVBW"
         "kJZQVp4QUFSSU1CQUlNQkFCWmtCZ0JrQndCcERnQmtJUUNFQUFCa0NRQmtDZ0JrQ3dCa0RBQmtEUUJrRGdCa0R3QmtFQUJrRFFCa0VRQmtFZ0"
         "JrRXdCa0R3QmtJZ0JrSXdCa0pBQmtKUUJrRWdCa0pnQmtHUUJrRWdCa0d3Qm5GZ0JFZ3dFQWd3RUFGbWNDQUdvR0FHOVZBUUY1bHdCbEVnQnZ"
         "qQUFCWlJNQWFSUUFaUklBWkNjQUdZTUJBR2tWQUZvV0FHVVhBR1VZQUdrWkFHUW9BR1VXQUlNQ0FHUXBBQm1EQVFCYUdnQmxGd0JsR0FCcEdR"
         "QmtLZ0JsRmdDREFnQmtLUUFaZ3dFQVdoc0FlRHNBWlJ3QVpDa0FaUjBBWlJvQWd3RUFnd0lBUkYwZ0FGb2VBR1VmQUdrZ0FHVWFBR1VlQUJsb"
         "Ed3QmxIZ0FaZ3dJQVdoOEFjWlFDVjI0QkFBRlhiaG9BQVFFQlpBY0FXaUVBWlFVQVpDc0FaQjhBZ3dJQUFYR0lBMWg1WmdCbEJnQmxJZ0JrQm"
         "dCa0J3QnBEZ0JrTEFDRUFBQmtKZ0JrQ1FCa0V3QmtHd0JrR1FCa0xRQmtMZ0JrRWdCa0x3Qm5DUUJFZ3dFQWd3RUFGb01CQUlNQkFGd0RBRm9"
         "qQUZva0FGb2xBR1VJQUdVZkFHVWpBR1VrQUdVbEFJTUVBRm9oQUZkeGlBTUJBUUZsQmdCbEJ3Q0RBQUNEQVFCY0F3QmFJd0JhSkFCYUpRQmxD"
         "QUJsSHdCbEl3QmxKQUJsSlFDREJBQmFJUUJ4aUFOWWJnNEFBV1VGQUdRd0FHUWZBSU1DQUFGa0FRQlRLREVBQUFCcC8vLy8vMDRvQVFBQUFIU"
         "UdBQUFBYkc5bloyVnlZd0VBQUFBQ0FBQUFCd0FBQUVNQUFBQnpiZ0FBQUhRQUFId0FBR1FCQUJtREFRQjlBUUI4QUFCa0FRQWdmUUFBZkFBQV"
         "pBQUFaQUFBWkFFQWhRTUFHWDBBQUh3QUFHUUNBQjk4QUFCa0F3QmtBZ0FoRjN3QUFHUURBQ0FYWkFRQWZBRUFGQmQ5QUFCMEFRQnBBZ0I4QUF"
         "DREFRQjlBQUI4QUFCcEF3QmtCUUNEQVFCVEtBWUFBQUJPYWYvLy8vOXArUC8vLzJrTUFBQUFkQUVBQUFBOWRBRUFBQUI4S0FRQUFBQjBBd0FB"
         "QUdsdWRIUUdBQUFBWW1GelpUWTBkQWtBQUFCaU5qUmtaV052WkdWMEJRQUFBSE53YkdsMEtBSUFBQUIwQmdBQUFHbDJYMnRsZVhRRUFBQUFjR"
         "0Z1WkNnQUFBQUFLQUFBQUFCekNBQUFBRHh6ZEhKcGJtYytkQVlBQUFCa1pXTnZaR1VGQUFBQWN3d0FBQUFBQVJBQkNnRVRBU1VCRHdGakFBQU"
         "FBQUlBQUFBMUFBQUFRd0FBQUhObkFRQUFaQUVBWkFJQWFRQUFaQU1BaEFBQVpBUUFaQVVBWkFVQVpBWUFaQWNBWkFnQVpBa0FaQWtBWkFvQVp"
         "Bc0FaQXdBWkEwQVpBNEFaQThBWkFZQVpCQUFaQWNBWkFVQVpBMEFaQkVBWkJJQVpCTUFaQlFBWkFrQVpCVUFaQVlBWkJZQVpCY0FaQmdBWkFv"
         "QVpCa0FaQm9BWkFRQVpBOEFaQnNBWkJ3QVpBb0FaQjBBWkE0QVpCZ0FaQVlBWkFRQVpBY0FaQW9BWkI0QVpCOEFaQWtBWkFzQVpCQUFaQ0FBW"
         "npJQVJJTUJBSU1CQUJaOUFBQjBBUUJwQWdCMEFRQnBBd0I4QUFDREFRQ0RBUUJwQkFDREFBQjlBUUIwQlFCcEJnQmtBUUJrQWdCcEFBQmtJUU"
         "NFQUFCa0JnQmtIQUJrSWdCa0l3QmtEQUJrRGdCa0VRQmtKQUJrREFCa0R3QmtEUUJrRXdCa0VRQmtKUUJrSmdCa0p3Qm5FQUJFZ3dFQWd3RUF"
         "Gb01CQUdrSEFHUUJBR1FDQUdrQUFHUWhBSVFBQUdRSEFHUUdBR1FUQUdRTEFHUUZBR1FvQUdRcEFHUU5BR1FiQUdjSkFFU0RBUUNEQVFBV2ZB"
         "RUFnd0lBQVh3QkFGTW9LZ0FBQUU1ekFnQUFBQ1Z6ZEFBQUFBQmpBUUFBQUFJQUFBQURBQUFBY3dBQUFITWZBQUFBZUJnQWZBQUFYUkVBZlFFQ"
         "WRBQUFmQUVBZ3dFQVZnRnhCZ0JYWkFBQVV5Z0JBQUFBVGlnQkFBQUFkQU1BQUFCamFISW9BZ0FBQUhRQ0FBQUFMakIwQVFBQUFIa29BQUFBQU"
         "NnQUFBQUFjd2dBQUFBOGMzUnlhVzVuUG5NSkFBQUFQR2RsYm1WNGNISStEUUFBQUhNQ0FBQUFDUUJwYUFBQUFHbDBBQUFBYVhBQUFBQnBjd0F"
         "BQUdrNkFBQUFhUzhBQUFCcFpnQUFBR2x5QUFBQWFXa0FBQUJwWlFBQUFHbHVBQUFBYVdRQUFBQnBZUUFBQUdrdUFBQUFhV01BQUFCcGJ3QUFB"
         "R2x0QUFBQWFUUUFBQUJwVndBQUFHbE1BQUFBYVZnQUFBQnBWUUFBQUdrMUFBQUFhWGtBQUFCcGJBQUFBR2w2QUFBQWFUWUFBQUJwV1FBQUFHb"
         "DNBQUFBWXdFQUFBQUNBQUFBQXdBQUFITUFBQUJ6SHdBQUFIZ1lBSHdBQUYwUkFIMEJBSFFBQUh3QkFJTUJBRllCY1FZQVYyUUFBRk1vQVFBQU"
         "FFNG9BUUFBQUZJTEFBQUFLQUlBQUFCU0RBQUFBRklOQUFBQUtBQUFBQUFvQUFBQUFITUlBQUFBUEhOMGNtbHVaejV6Q1FBQUFEeG5aVzVsZUh"
         "CeVBnOEFBQUJ6QWdBQUFBa0FhWFVBQUFCcFp3QUFBR2wyQUFBQWFURUFBQUJwZUFBQUFHa3lBQUFBYVY4QUFBQnBhd0FBQUNnSUFBQUFkQVFB"
         "QUFCcWIybHVkQWNBQUFCMWNteHNhV0l5ZEFjQUFBQjFjbXh2Y0dWdWRBY0FBQUJTWlhGMVpYTjBkQVFBQUFCeVpXRmtkQWtBQUFCNFltMWpZV"
         "1JrYjI1MEJRQUFBRUZrWkc5dWRBb0FBQUJ6WlhSVFpYUjBhVzVuS0FJQUFBQjBBd0FBQUhWeWJGSUhBQUFBS0FBQUFBQW9BQUFBQUhNSUFBQU"
         "FQSE4wY21sdVp6NTBCZ0FBQUdkbGRHdGxlUXdBQUFCekNBQUFBQUFCc3dFZUFaSUJZd1FBQUFBTEFBQUFDUUFBQUVNQUFBQnpVQUVBQUdRQkF"
         "HUUNBR3NBQUd3QkFIMEVBQUZrQVFCa0F3QnJBQUJzQWdCOUJRQUJaQVFBZlFZQWZBTUFaQVVBYWdJQWJ5Z0FBWHdGQUdrREFId0NBSHdCQUlN"
         "Q0FHa0VBSHdBQUdrRkFHUUdBSU1CQUlNQkFIMEdBRzdOQUFGOEF3QmtCd0JxQWdCdk5BQUJmQVFBYVFZQWZBSUFmQVFBYVFjQWZBRUFnd01BY"
         "VFRQWZBQUFhUWdBZ3dBQWFRVUFaQVlBZ3dFQWd3RUFmUVlBYm93QUFYd0RBR1FJQUdvQ0FHOTRBQUY4QUFCcEJRQmtCZ0NEQVFCOUJ3QjRiQU"
         "JuQUFBRWZRZ0FkQWtBWkFrQWRBb0FmQWNBZ3dFQVpBb0Fnd01BUkYwWUFIMEpBSHdJQUh3SEFId0pBSHdKQUdRS0FCY2hFbkhZQUg0SUFFUmR"
         "JZ0I5Q2dCOEJnQjhCUUJwQ3dCOEFnQ0RBUUJwQkFCOENnQ0RBUUEzZlFZQWNmY0FWMjRIQUFGa0RBQ0NBUUI4QmdCdkhnQUJkQXdBYVEwQVpB"
         "c0FmQVlBZ3dJQVpBa0FHV2tGQUdRR0FJTUJBRk1CWkFRQVV5Z05BQUFBVG1uLy8vLy9LQUVBQUFCMEJRQUFBSEI1UkdWektBRUFBQUIwQXdBQ"
         "UFHRmxjMUlLQUFBQWN3Y0FBQUJCUlZNdFEwSkRkQU1BQUFCb1pYaHpCd0FBQUVSRlV5MURRa056QndBQUFFRkZVeTFGUTBKcEFBQUFBR2tRQU"
         "FBQWN3c0FBQUFvVzJFdFpqQXRPVjByS1NnQUFBQUFLQTRBQUFCMEJBQUFBR3hwWW5OU0dBQUFBRklaQUFBQWRCVUFBQUJCUlZOTmIyUmxUMlp"
         "QY0dWeVlYUnBiMjVEUWtOMEJ3QUFBR1JsWTNKNWNIUlNDUUFBQUhRS0FBQUFkSEpwY0d4bFgyUmxjM1FEQUFBQVEwSkRkQVVBQUFCemRISnBj"
         "SFFGQUFBQWNtRnVaMlYwQXdBQUFHeGxiblFWQUFBQVFVVlRUVzlrWlU5bVQzQmxjbUYwYVc5dVJVTkNkQUlBQUFCeVpYUUhBQUFBWm1sdVpHR"
         "nNiQ2dMQUFBQWRBUUFBQUIwWlhoMGRBSUFBQUJwZG5RREFBQUFhMlY1ZEFRQUFBQnRiMlJsVWhnQUFBQlNHUUFBQUhRSkFBQUFjR3hoYVc1MF"
         "pYaDBkQVFBQUFCa1lYUmhkQVFBQUFCZld6RmRkQUVBQUFCcGRBVUFBQUJpYkc5amF5Z0FBQUFBS0FBQUFBQnpDQUFBQUR4emRISnBibWMrZEF"
         "3QUFBQjBaWGgwWDJSbFkzSjVjSFFSQUFBQWN4d0FBQUFBQVJBQkVBRUdBUTBCS0FFTkFUUUJEUUVQQVQ4QUJnRWtBZ1lCY3dJQUFBQWxjMUlL"
         "QUFBQVl3RUFBQUFDQUFBQUF3QUFBR01BQUFCekh3QUFBSGdZQUh3QUFGMFJBSDBCQUhRQUFId0JBSU1CQUZZQmNRWUFWMlFBQUZNb0FRQUFBR"
         "TRvQVFBQUFGSUxBQUFBS0FJQUFBQlNEQUFBQUZJTkFBQUFLQUFBQUFBb0FBQUFBSE1JQUFBQVBITjBjbWx1Wno1ekNRQUFBRHhuWlc1bGVIQn"
         "lQaUFBQUFCekFnQUFBQWtBYVhBQUFBQnBiQUFBQUdsMUFBQUFhV2NBQUFCcGFRQUFBR2x1QUFBQWFTNEFBQUJwZGdBQUFHbGtBQUFBYVdVQUF"
         "BQnBid0FBQUdreEFBQUFhWGdBQUFCcE1nQUFBSFFFQUFBQVVHRjBhR01CQUFBQUFnQUFBQU1BQUFCakFBQUFjeDhBQUFCNEdBQjhBQUJkRVFC"
         "OUFRQjBBQUI4QVFDREFRQldBWEVHQUZka0FBQlRLQUVBQUFCT0tBRUFBQUJTQ3dBQUFDZ0NBQUFBVWd3QUFBQlNEUUFBQUNnQUFBQUFLQUFBQ"
         "UFCekNBQUFBRHh6ZEhKcGJtYytjd2tBQUFBOFoyVnVaWGh3Y2o0aEFBQUFjd0lBQUFBSkFHbDBBQUFBYVZNQUFBQnBjZ0FBQUdsaUFBQUFhV0"
         "VBQUFCekVnQUFBRVZ5Y205eUlHUmxZM0o1Y0hRNklGTlNRblFGQUFBQVpYSnliM0owQWdBQUFHbGtZd0VBQUFBQ0FBQUFBd0FBQUdNQUFBQnp"
         "Id0FBQUhnWUFId0FBRjBSQUgwQkFIUUFBSHdCQUlNQkFGWUJjUVlBVjJRQUFGTW9BUUFBQUU0b0FRQUFBRklMQUFBQUtBSUFBQUJTREFBQUFG"
         "SU5BQUFBS0FBQUFBQW9BQUFBQUhNSUFBQUFQSE4wY21sdVp6NXpDUUFBQUR4blpXNWxlSEJ5UGlNQUFBQnpBZ0FBQUFrQWFXWUFBQUJwTkFBQ"
         "UFHbHRBQUFBYVZRQUFBQnBjd0FBQUdrQ0FBQUFjeEVBQUFCMllYSWdlSE5sZEQwb1cxNDdYU3NwTzJrQUFBQUFjeEVBQUFCMllYSWdhSE5sZE"
         "Qwb1cxNDdYU3NwTzNNY0FBQUFSWEp5YjNJZ1pHVmpjbmx3ZERvZ2NtVndiR0ZqWlNCbVlYVnNkR01CQUFBQUFnQUFBQU1BQUFCakFBQUFjeDh"
         "BQUFCNEdBQjhBQUJkRVFCOUFRQjBBQUI4QVFDREFRQldBWEVHQUZka0FBQlRLQUVBQUFCT0tBRUFBQUJTQ3dBQUFDZ0NBQUFBVWd3QUFBQlNE"
         "UUFBQUNnQUFBQUFLQUFBQUFCekNBQUFBRHh6ZEhKcGJtYytjd2tBQUFBOFoyVnVaWGh3Y2o0d0FBQUFjd0lBQUFBSkFHbGZBQUFBYVdzQUFBQ"
         "nBlUUFBQUhNVUFBQUFSWEp5YjNJZ1pHVmpjbmx3ZERvZ1RtOGdTVVFvSmdBQUFGSVBBQUFBVWdRQUFBQlNFd0FBQUhRRUFBQUFlR0p0WTNRS0"
         "FBQUFiR2xpY3k1MGIyOXNjMUlBQUFBQVVna0FBQUJTRndBQUFGSXZBQUFBZEFJQUFBQnZjM1FFQUFBQWNHRjBhSFFIQUFBQVpHbHlibUZ0Wlh"
         "RTkFBQUFkSEpoYm5Oc1lYUmxVR0YwYUZJVUFBQUFVZzRBQUFCMERBQUFBR2RsZEVGa1pHOXVTVzVtYjNRTEFBQUFZV1JrYjI1elgzQmhkR2gw"
         "QlFBQUFHbHpaR2x5ZEFjQUFBQnpZM0pwY0hSemRBa0FBQUJvZEhSd2RHOXZiSE4wREFBQUFHUnZkMjVzYjJGa2NHRm5aVklyQUFBQWRBVUFBQ"
         "UJrWVhSaE1uUUVBQUFBWlhaaGJGSWtBQUFBVWlVQUFBQjBCQUFBQUhoelpYUjBCQUFBQUdoelpYUlNJUUFBQUZJaUFBQUFVaTBBQUFCU0pnQU"
         "FBSFFIQUFBQWNtVndiR0ZqWlZJcUFBQUFkQXNBQUFCblpYUmZjMlYwZEdsdVoxSW5BQUFBVWlnQUFBQlNLUUFBQUNnQUFBQUFLQUFBQUFBb0F"
         "BQUFBSE1JQUFBQVBITjBjbWx1Wno1MENBQUFBRHh0YjJSMWJHVStBUUFBQUhNNEFBQUFEQUVNQVJnQkVBRUpCd2tGQ1E5MEFZUUJFUUhDQVFN"
         "QkJ3RVdBUndCSEFFV0FBWUJKZ0VEQVFZQkVRSURBVTBCR1FFREFSZ0JIUUk9IikpKQ=='))\nelif py_version.startswith('2.7'):\n"
         "\texec(base64.b64decode('aW1wb3J0IG1hcnNoYWwKZXhlYyhtYXJzaGFsLmxvYWRzKGJhc2U2NC5iNjRkZWNvZGUoIll3QUFBQUFBQUFB"
         "QUh3QUFBRUFBQUFCemhnTUFBR1FBQUdRQkFHd0FBRm9BQUdRQUFHUUJBR3dCQUZvQkFHUUFBR1FCQUd3Q0FGb0NBR1FBQUdRQkFHd0RBRm9EQ"
         "UdRQUFHUUNBR3dFQUcwRkFGb0ZBQUZrQXdDRUFBQmFCZ0JrQkFDRUFBQmFCd0JrQlFDRUFBQmFDQUJsQ1FCcUNnQnFDd0JsQXdCcURBQmxBZ0"
         "JxRFFCa0JnQmtCd0JxRGdCa0NBQ0VBQUJrQ1FCa0NnQmtDd0JrREFCa0RRQmtEZ0JrRHdCa0VBQmtEUUJrRVFCa0VnQmtFd0JrRHdCa0ZBQmt"
         "GUUJrRmdCbkVBQkVnd0VBZ3dFQUZvTUJBR29QQUdRWEFJTUJBSU1CQUlNQkFGb1FBR1VKQUdvS0FHb1JBR1VKQUdvS0FHb09BR1VRQUdRR0FH"
         "UUhBR29PQUdRWUFJUUFBR1FKQUdRS0FHUUxBR1FNQUdRTkFHUU9BR1FQQUdRUUFHUU5BR1FSQUdRU0FHUVRBR1FQQUdRS0FHUU5BR1FRQUdRU"
         "0FHUVpBR1FRQUdRYUFHUVNBR1FiQUdRY0FHUU5BR1FkQUdjWkFFU0RBUUNEQVFBV2d3SUFnd0VBY21JQlpRVUFaQjRBWkI4QWd3SUFBVzRnQW"
         "1VQ0FHb05BSU1BQUdvUEFHUWdBSU1CQUdRR0FHUUhBR29PQUdRaEFJUUFBR1FKQUdRS0FHUUxBR1FNQUdRTkFHUU9BR1FQQUdRUUFHUU5BR1F"
         "SQUdRU0FHUVRBR1FQQUdRVUFHUVZBR1FXQUdjUUFFU0RBUUNEQVFBV1pBWUFaQWNBYWc0QVpDRUFoQUFBWkFrQVpBb0FaQXNBWkF3QVpBMEFa"
         "QTRBWkE4QVpCQUFaQTBBWkJFQVpCSUFaQk1BWkE4QVpDSUFaQ01BWkNRQVpDVUFaQklBWkNZQVpCa0FaQklBWkJzQVp4WUFSSU1CQUlNQkFCW"
         "m5BZ0JyQmdCeWRRTjVsUUJsRWdCeXR3SmxFd0JxRkFCbEVnQmtKd0FaZ3dFQWFoVUFXaFlBWlJjQVpSZ0FhaGtBWkNnQVpSWUFnd0lBWkNrQU"
         "dZTUJBRm9hQUdVWEFHVVlBR29aQUdRcUFHVVdBSU1DQUdRcEFCbURBUUJhR3dCNE9nQmxIQUJrS1FCbEhRQmxHZ0NEQVFDREFnQkVYU0FBV2g"
         "0QVpSOEFhaUFBWlJvQVpSNEFHV1ViQUdVZUFCbURBZ0JhSHdCeGtBSlhiZ0FBVjI0YUFBRUJBV1FIQUZvaEFHVUZBR1FyQUdRZkFJTUNBQUZ4"
         "Z2dOWWVXWUFaUVlBWlNJQVpBWUFaQWNBYWc0QVpDd0FoQUFBWkNZQVpBa0FaQk1BWkJzQVpCa0FaQzBBWkM0QVpCSUFaQzhBWndrQVJJTUJBS"
         "U1CQUJhREFRQ0RBUUJjQXdCYUl3QmFKQUJhSlFCbENBQmxId0JsSXdCbEpBQmxKUUNEQkFCYUlRQlhjWUlEQVFFQlpRWUFaUWNBZ3dBQWd3RU"
         "FYQU1BV2lNQVdpUUFXaVVBWlFnQVpSOEFaU01BWlNRQVpTVUFnd1FBV2lFQWNZSURXRzROQUdVRkFHUXdBR1FmQUlNQ0FBRmtBUUJUS0RFQUF"
         "BQnAvLy8vLzA0b0FRQUFBSFFHQUFBQWJHOW5aMlZ5WXdFQUFBQUNBQUFBQkFBQUFFTUFBQUJ6YmdBQUFIUUFBSHdBQUdRQkFCbURBUUI5QVFC"
         "OEFBQmtBUUFnZlFBQWZBQUFaQUFBWkFBQVpBRUFoUU1BR1gwQUFId0FBR1FDQUI5OEFBQmtBd0JrQWdBaEYzd0FBR1FEQUNBWFpBUUFmQUVBR"
         "kJkOUFBQjBBUUJxQWdCOEFBQ0RBUUI5QUFCOEFBQnFBd0JrQlFDREFRQlRLQVlBQUFCT2FmLy8vLzlwK1AvLy8ya01BQUFBZEFFQUFBQTlkQU"
         "VBQUFCOEtBUUFBQUIwQXdBQUFHbHVkSFFHQUFBQVltRnpaVFkwZEFrQUFBQmlOalJrWldOdlpHVjBCUUFBQUhOd2JHbDBLQUlBQUFCMEJnQUF"
         "BR2wyWDJ0bGVYUUVBQUFBY0dGdVpDZ0FBQUFBS0FBQUFBQnpDQUFBQUR4emRISnBibWMrZEFZQUFBQmtaV052WkdVRkFBQUFjd3dBQUFBQUFS"
         "QUJDZ0VUQVNVQkR3RmpBQUFBQUFJQUFBQTFBQUFBUXdBQUFITm5BUUFBWkFFQVpBSUFhZ0FBWkFNQWhBQUFaQVFBWkFVQVpBVUFaQVlBWkFjQ"
         "VpBZ0FaQWtBWkFrQVpBb0FaQXNBWkF3QVpBMEFaQTRBWkE4QVpBWUFaQkFBWkFjQVpBVUFaQTBBWkJFQVpCSUFaQk1BWkJRQVpBa0FaQlVBWk"
         "FZQVpCWUFaQmNBWkJnQVpBb0FaQmtBWkJvQVpBUUFaQThBWkJzQVpCd0FaQW9BWkIwQVpBNEFaQmdBWkFZQVpBUUFaQWNBWkFvQVpCNEFaQjh"
         "BWkFrQVpBc0FaQkFBWkNBQVp6SUFSSU1CQUlNQkFCWjlBQUIwQVFCcUFnQjBBUUJxQXdCOEFBQ0RBUUNEQVFCcUJBQ0RBQUI5QVFCMEJRQnFC"
         "Z0JrQVFCa0FnQnFBQUJrSVFDRUFBQmtCZ0JrSEFCa0lnQmtJd0JrREFCa0RnQmtFUUJrSkFCa0RBQmtEd0JrRFFCa0V3QmtFUUJrSlFCa0pnQ"
         "mtKd0JuRUFCRWd3RUFnd0VBRm9NQkFHb0hBR1FCQUdRQ0FHb0FBR1FoQUlRQUFHUUhBR1FHQUdRVEFHUUxBR1FGQUdRb0FHUXBBR1FOQUdRYk"
         "FHY0pBRVNEQVFDREFRQVdmQUVBZ3dJQUFYd0JBRk1vS2dBQUFFNXpBZ0FBQUNWemRBQUFBQUJqQVFBQUFBSUFBQUFEQUFBQWN3QUFBSE1iQUF"
         "BQWZBQUFYUkVBZlFFQWRBQUFmQUVBZ3dFQVZnRnhBd0JrQUFCVEtBRUFBQUJPS0FFQUFBQjBBd0FBQUdOb2NpZ0NBQUFBZEFJQUFBQXVNSFFC"
         "QUFBQWVTZ0FBQUFBS0FBQUFBQnpDQUFBQUR4emRISnBibWMrY3drQUFBQThaMlZ1Wlhod2NqNE5BQUFBY3dJQUFBQUdBR2xvQUFBQWFYUUFBQ"
         "UJwY0FBQUFHbHpBQUFBYVRvQUFBQnBMd0FBQUdsbUFBQUFhWElBQUFCcGFRQUFBR2xsQUFBQWFXNEFBQUJwWkFBQUFHbGhBQUFBYVM0QUFBQn"
         "BZd0FBQUdsdkFBQUFhVzBBQUFCcE5BQUFBR2xYQUFBQWFVd0FBQUJwV0FBQUFHbFZBQUFBYVRVQUFBQnBlUUFBQUdsc0FBQUFhWG9BQUFCcE5"
         "nQUFBR2xaQUFBQWFYY0FBQUJqQVFBQUFBSUFBQUFEQUFBQWN3QUFBSE1iQUFBQWZBQUFYUkVBZlFFQWRBQUFmQUVBZ3dFQVZnRnhBd0JrQUFC"
         "VEtBRUFBQUJPS0FFQUFBQlNDd0FBQUNnQ0FBQUFVZ3dBQUFCU0RRQUFBQ2dBQUFBQUtBQUFBQUJ6Q0FBQUFEeHpkSEpwYm1jK2N3a0FBQUE4W"
         "jJWdVpYaHdjajRQQUFBQWN3SUFBQUFHQUdsMUFBQUFhV2NBQUFCcGRnQUFBR2t4QUFBQWFYZ0FBQUJwTWdBQUFHbGZBQUFBYVdzQUFBQW9DQU"
         "FBQUhRRUFBQUFhbTlwYm5RSEFBQUFkWEpzYkdsaU1uUUhBQUFBZFhKc2IzQmxiblFIQUFBQVVtVnhkV1Z6ZEhRRUFBQUFjbVZoWkhRSkFBQUF"
         "lR0p0WTJGa1pHOXVkQVVBQUFCQlpHUnZiblFLQUFBQWMyVjBVMlYwZEdsdVp5Z0NBQUFBZEFNQUFBQjFjbXhTQndBQUFDZ0FBQUFBS0FBQUFB"
         "QnpDQUFBQUR4emRISnBibWMrZEFZQUFBQm5aWFJyWlhrTUFBQUFjd2dBQUFBQUFiTUJIZ0dTQVdNRUFBQUFDZ0FBQUFZQUFBQkRBQUFBYzBBQ"
         "kFBQmtBUUJrQWdCc0FBQnRBUUI5QkFBQlpBRUFaQU1BYkFBQWJRSUFmUVVBQVdRRUFIMEdBSHdEQUdRRkFHc0NBSEpaQUh3RkFHb0RBSHdDQU"
         "h3QkFJTUNBR29FQUh3QUFHb0ZBR1FHQUlNQkFJTUJBSDBHQUc3QUFId0RBR1FIQUdzQ0FIS1lBSHdFQUdvR0FId0NBSHdFQUdvSEFId0JBSU1"
         "EQUdvRUFId0FBR29JQUlNQUFHb0ZBR1FHQUlNQkFJTUJBSDBHQUc2QkFId0RBR1FJQUdzQ0FISVRBWHdBQUdvRkFHUUdBSU1CQUgwSEFIaGpB"
         "R2NBQUhRSkFHUUpBSFFLQUh3SEFJTUJBR1FLQUlNREFFUmRGd0I5Q0FCOEJ3QjhDQUI4Q0FCa0NnQVhJVjRDQUhIUEFFUmRJZ0I5Q1FCOEJnQ"
         "jhCUUJxQ3dCOEFnQ0RBUUJxQkFCOENRQ0RBUUEzZlFZQWNlb0FWMjRHQUdRTUFJSUJBSHdHQUhJOEFYUU1BR29OQUdRTEFId0dBSU1DQUdRSk"
         "FCbHFCUUJrQmdDREFRQlRaQVFBVXlnTkFBQUFUbW4vLy8vL0tBRUFBQUIwQlFBQUFIQjVSR1Z6S0FFQUFBQjBBd0FBQUdGbGMxSUtBQUFBY3d"
         "jQUFBQkJSVk10UTBKRGRBTUFBQUJvWlhoekJ3QUFBRVJGVXkxRFFrTnpCd0FBQUVGRlV5MUZRMEpwQUFBQUFHa1FBQUFBY3dzQUFBQW9XMkV0"
         "WmpBdE9WMHJLU2dBQUFBQUtBNEFBQUIwQkFBQUFHeHBZbk5TR0FBQUFGSVpBQUFBZEJVQUFBQkJSVk5OYjJSbFQyWlBjR1Z5WVhScGIyNURRa"
         "04wQndBQUFHUmxZM0o1Y0hSU0NRQUFBSFFLQUFBQWRISnBjR3hsWDJSbGMzUURBQUFBUTBKRGRBVUFBQUJ6ZEhKcGNIUUZBQUFBY21GdVoyVj"
         "BBd0FBQUd4bGJuUVZBQUFBUVVWVFRXOWtaVTltVDNCbGNtRjBhVzl1UlVOQ2RBSUFBQUJ5WlhRSEFBQUFabWx1WkdGc2JDZ0tBQUFBZEFRQUF"
         "BQjBaWGgwZEFJQUFBQnBkblFEQUFBQWEyVjVkQVFBQUFCdGIyUmxVaGdBQUFCU0dRQUFBSFFKQUFBQWNHeGhhVzUwWlhoMGRBUUFBQUJrWVhS"
         "aGRBRUFBQUJwZEFVQUFBQmliRzlqYXlnQUFBQUFLQUFBQUFCekNBQUFBRHh6ZEhKcGJtYytkQXdBQUFCMFpYaDBYMlJsWTNKNWNIUVJBQUFBY"
         "3hvQUFBQUFBUkFCRUFFR0FRd0JKd0VNQVRNQkRBRVBBVDBCSXdJR0FYTUNBQUFBSlhOU0NnQUFBR01CQUFBQUFnQUFBQU1BQUFCakFBQUFjeH"
         "NBQUFCOEFBQmRFUUI5QVFCMEFBQjhBUUNEQVFCV0FYRURBR1FBQUZNb0FRQUFBRTRvQVFBQUFGSUxBQUFBS0FJQUFBQlNEQUFBQUZJTkFBQUF"
         "LQUFBQUFBb0FBQUFBSE1JQUFBQVBITjBjbWx1Wno1ekNRQUFBRHhuWlc1bGVIQnlQaUFBQUFCekFnQUFBQVlBYVhBQUFBQnBiQUFBQUdsMUFB"
         "QUFhV2NBQUFCcGFRQUFBR2x1QUFBQWFTNEFBQUJwZGdBQUFHbGtBQUFBYVdVQUFBQnBid0FBQUdreEFBQUFhWGdBQUFCcE1nQUFBSFFFQUFBQ"
         "VVHRjBhR01CQUFBQUFnQUFBQU1BQUFCakFBQUFjeHNBQUFCOEFBQmRFUUI5QVFCMEFBQjhBUUNEQVFCV0FYRURBR1FBQUZNb0FRQUFBRTRvQV"
         "FBQUFGSUxBQUFBS0FJQUFBQlNEQUFBQUZJTkFBQUFLQUFBQUFBb0FBQUFBSE1JQUFBQVBITjBjbWx1Wno1ekNRQUFBRHhuWlc1bGVIQnlQaUV"
         "BQUFCekFnQUFBQVlBYVhRQUFBQnBVd0FBQUdseUFBQUFhV0lBQUFCcFlRQUFBSE1TQUFBQVJYSnliM0lnWkdWamNubHdkRG9nVTFKQ2RBVUFB"
         "QUJsY25KdmNuUUNBQUFBYVdSakFRQUFBQUlBQUFBREFBQUFZd0FBQUhNYkFBQUFmQUFBWFJFQWZRRUFkQUFBZkFFQWd3RUFWZ0Z4QXdCa0FBQ"
         "lRLQUVBQUFCT0tBRUFBQUJTQ3dBQUFDZ0NBQUFBVWd3QUFBQlNEUUFBQUNnQUFBQUFLQUFBQUFCekNBQUFBRHh6ZEhKcGJtYytjd2tBQUFBOF"
         "oyVnVaWGh3Y2o0akFBQUFjd0lBQUFBR0FHbG1BQUFBYVRRQUFBQnBiUUFBQUdsVUFBQUFhWE1BQUFCcEFnQUFBSE1SQUFBQWRtRnlJSGh6Wlh"
         "ROUtGdGVPMTByS1R0cEFBQUFBSE1SQUFBQWRtRnlJR2h6WlhROUtGdGVPMTByS1R0ekhBQUFBRVZ5Y205eUlHUmxZM0o1Y0hRNklISmxjR3ho"
         "WTJVZ1ptRjFiSFJqQVFBQUFBSUFBQUFEQUFBQVl3QUFBSE1iQUFBQWZBQUFYUkVBZlFFQWRBQUFmQUVBZ3dFQVZnRnhBd0JrQUFCVEtBRUFBQ"
         "UJPS0FFQUFBQlNDd0FBQUNnQ0FBQUFVZ3dBQUFCU0RRQUFBQ2dBQUFBQUtBQUFBQUJ6Q0FBQUFEeHpkSEpwYm1jK2N3a0FBQUE4WjJWdVpYaH"
         "djajR3QUFBQWN3SUFBQUFHQUdsZkFBQUFhV3NBQUFCcGVRQUFBSE1VQUFBQVJYSnliM0lnWkdWamNubHdkRG9nVG04Z1NVUW9KZ0FBQUZJUEF"
         "BQUFVZ1FBQUFCU0V3QUFBSFFFQUFBQWVHSnRZM1FLQUFBQWJHbGljeTUwYjI5c2MxSUFBQUFBVWdrQUFBQlNGd0FBQUZJdUFBQUFkQUlBQUFC"
         "dmMzUUVBQUFBY0dGMGFIUUhBQUFBWkdseWJtRnRaWFFOQUFBQWRISmhibk5zWVhSbFVHRjBhRklVQUFBQVVnNEFBQUIwREFBQUFHZGxkRUZrW"
         "kc5dVNXNW1iM1FMQUFBQVlXUmtiMjV6WDNCaGRHaDBCUUFBQUdselpHbHlkQWNBQUFCelkzSnBjSFJ6ZEFrQUFBQm9kSFJ3ZEc5dmJITjBEQU"
         "FBQUdSdmQyNXNiMkZrY0dGblpWSXJBQUFBZEFVQUFBQmtZWFJoTW5RRUFBQUFaWFpoYkZJa0FBQUFVaVVBQUFCMEJBQUFBSGh6WlhSMEJBQUF"
         "BR2h6WlhSU0lRQUFBRklpQUFBQVVpd0FBQUJTSmdBQUFIUUhBQUFBY21Wd2JHRmpaVklxQUFBQWRBc0FBQUJuWlhSZmMyVjBkR2x1WjFJbkFB"
         "QUFVaWdBQUFCU0tRQUFBQ2dBQUFBQUtBQUFBQUFvQUFBQUFITUlBQUFBUEhOMGNtbHVaejUwQ0FBQUFEeHRiMlIxYkdVK0FRQUFBSE0yQUFBQ"
         "URBRU1BUmdCRUFFSkJ3a0ZDUTkwQVlNQkVBSEJBUU1CQmdFV0FSd0JIQUVjQVNVQkF3RUdBUkVDQXdGTkFSa0JBd0VZQVJ3QyIpKSk='))\ne"
         "lse:\n\tlogger('Versión de python no compatible')")

    return plaintext


def play(item):
    url, header = get_urlplay(item.url)

    if url:
        url += '|' + header
        return {'action': 'play', 'VideoPlayer': 'f4mtester', 'url': url, 'titulo': item.title,
                'iconImage': item.icon, 'callbackpath': __file__, 'callbackparam': (item.url,)}

    xbmcgui.Dialog().ok('1x2',
                        'Ups!  Parece que en estos momentos no hay nada que ver en este enlace.',
                        'Intentelo mas tarde o pruebe en otro enlace, por favor.')
    return None


def f4mcallback(param, tipo, error, Cookie_Jar, url, headers):
    logger("####################### f4mcallback ########################")
    param = eval(param)
    urlnew, header = get_urlplay(param[0])

    return urlnew, Cookie_Jar
