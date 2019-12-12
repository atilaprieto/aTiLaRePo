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

            guide.append(Evento(fecha=fecha, hora=hora, formatTime='CEST', deltaTime=-1, sport=deporte,
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

            url = decrypt(data)
            if not url: raise ()

            url_head = 'User-Agent=%s&Referer=%s' % (
                urllib.quote(httptools.default_headers["User-Agent"]), urllib.quote('http://h5.adshell.net/peer5'))

            return (url, url_head)
    except:
        logger("Error in get_url", 'error')
        return (None, None)


def decrypt(text):
    plaintext = ''
    exec("import base64\nfrom libs.tools import *\nif py_version.startswith('2.6'):\n\texec(base64.b64decode('aW1wb3J0I"
         "G1hcnNoYWwKZXhlYyhtYXJzaGFsLmxvYWRzKGJhc2U2NC5iNjRkZWNvZGUoIll3QUFBQUFBQUFBQUpRQUFBRUFBQUFCelF3TUFBR1FBQUdRQk"
         "FHc0FBRm9BQUdRQUFHUUJBR3NCQUZvQkFHUUFBR1FCQUdzQ0FGb0NBR1FBQUdRQkFHc0RBRm9EQUdRQUFHUUNBR3NFQUd3RkFGb0ZBQUZrQUF"
         "Ca0F3QnJCZ0JzQndCYUJ3QUJaQVFBaEFBQVdnZ0FaQVVBaEFBQVdna0FaUW9BYVFzQWFRd0FaUU1BYVEwQVpRSUFhUTRBWkFZQVpBY0FhUThB"
         "WkFnQWhBQUFaQWtBWkFvQVpBc0FaQXdBWkEwQVpBNEFaQThBWkJBQVpBMEFaQkVBWkJJQVpCTUFaQThBWkJRQVpCVUFaQllBWnhBQVJJTUJBS"
         "U1CQUJhREFRQnBFQUJrRndDREFRQ0RBUUNEQVFCYUVRQmxDZ0JwQ3dCcEVnQmxDZ0JwQ3dCcER3QmxFUUJrQmdCa0J3QnBEd0JrR0FDRUFBQm"
         "tDUUJrQ2dCa0N3QmtEQUJrRFFCa0RnQmtEd0JrRUFCa0RRQmtFUUJrRWdCa0V3QmtEd0JrQ2dCa0RRQmtFQUJrRWdCa0dRQmtFQUJrR2dCa0V"
         "nQmtHd0JrSEFCa0RRQmtIUUJuR1FCRWd3RUFnd0VBRm9NQ0FJTUJBRzhSQUFGbEJ3QmtIZ0JrSHdDREFnQUJidFVCQVdVQ0FHa09BSU1BQUdr"
         "UUFHUWdBSU1CQUdRR0FHUUhBR2tQQUdRaEFJUUFBR1FKQUdRS0FHUUxBR1FNQUdRTkFHUU9BR1FQQUdRUUFHUU5BR1FSQUdRU0FHUVRBR1FQQ"
         "UdRVUFHUVZBR1FXQUdjUUFFU0RBUUNEQVFBV1pBWUFaQWNBYVE4QVpDRUFoQUFBWkFrQVpBb0FaQXNBWkF3QVpBMEFaQTRBWkE4QVpCQUFaQT"
         "BBWkJFQVpCSUFaQk1BWkE4QVpDSUFaQ01BWkNRQVpDVUFaQklBWkNZQVpCa0FaQklBWkJzQVp4WUFSSU1CQUlNQkFCWm5BZ0JxQmdCdkJRRUJ"
         "lWkVBWlFrQVpSTUFaQVlBWkFjQWFROEFaQ2NBaEFBQVpDWUFaQWtBWkJNQVpCc0FaQmtBWkNnQVpDa0FaQklBWkNvQVp3a0FSSU1CQUlNQkFC"
         "YURBUUNEQVFCY0FnQmFGQUJhRlFCbEJRQnBGZ0JsRlFCbEZBQ0RBZ0JwRndCbEdBQnBDUUJrS3dDREFRQ0RBUUJhR1FCbEdnQnBHd0JrTEFCb"
         "EdRQ0RBZ0JrTFFBWmFRa0FaQ3NBZ3dFQVdoa0FWM0UvQXdFQkFYbFdBR1VJQUlNQUFGd0NBRm9VQUZvVkFHVUZBR2tXQUdVVkFHVVVBSU1DQU"
         "drWEFHVVlBR2tKQUdRckFJTUJBSU1CQUZvWkFHVWFBR2tiQUdRc0FHVVpBSU1DQUdRdEFCbHBDUUJrS3dDREFRQmFHUUJYY1M0REFRRUJaQWN"
         "BV2hrQWNTNERXSEUvQTFodURnQUJaUWNBWkM0QVpCOEFnd0lBQVdRQkFGTW9Md0FBQUduLy8vLy9UaWdCQUFBQWRBTUFBQUJoWlhNb0FRQUFB"
         "SFFHQUFBQWJHOW5aMlZ5WXdBQUFBQUNBQUFBTlFBQUFFTUFBQUJ6YlFFQUFHUUJBR1FDQUdrQUFHUURBSVFBQUdRRUFHUUZBR1FGQUdRR0FHU"
         "UhBR1FJQUdRSkFHUUpBR1FLQUdRTEFHUU1BR1FOQUdRT0FHUVBBR1FHQUdRUUFHUUhBR1FGQUdRTkFHUVJBR1FTQUdRVEFHUVVBR1FKQUdRVk"
         "FHUUdBR1FXQUdRWEFHUVlBR1FLQUdRWkFHUWFBR1FFQUdRUEFHUWJBR1FjQUdRS0FHUWRBR1FPQUdRWUFHUUdBR1FFQUdRSEFHUUtBR1FlQUd"
         "RZkFHUUpBR1FMQUdRUUFHUWdBR2N5QUVTREFRQ0RBUUFXZlFBQWRBRUFhUUlBZEFFQWFRTUFmQUFBZ3dFQWd3RUFhUVFBZ3dBQWZRRUFkQVVB"
         "YVFZQVpBRUFaQUlBYVFBQVpDRUFoQUFBWkFZQVpCd0FaQ0lBWkNNQVpBd0FaQTRBWkJFQVpDUUFaQXdBWkE4QVpBMEFaQk1BWkJFQVpDVUFaQ"
         "1lBWkNjQVp4QUFSSU1CQUlNQkFCYURBUUJwQndCa0FRQmtBZ0JwQUFCa0lRQ0VBQUJrQndCa0JnQmtFd0JrQ3dCa0JRQmtLQUJrS1FCa0RRQm"
         "tHd0JuQ1FCRWd3RUFnd0VBRm53QkFJTUNBQUYwQ0FCOEFRQ0RBUUJUS0NvQUFBQk9jd0lBQUFBbGMzUUFBQUFBWXdFQUFBQUNBQUFBQXdBQUF"
         "ITUFBQUJ6SHdBQUFIZ1lBSHdBQUYwUkFIMEJBSFFBQUh3QkFJTUJBRllCY1FZQVYyUUFBRk1vQVFBQUFFNG9BUUFBQUhRREFBQUFZMmh5S0FJ"
         "QUFBQjBBZ0FBQUM0d2RBRUFBQUI1S0FBQUFBQW9BQUFBQUhNSUFBQUFQSE4wY21sdVp6NXpDUUFBQUR4blpXNWxlSEJ5UGdjQUFBQnpBZ0FBQ"
         "UFrQWFXZ0FBQUJwZEFBQUFHbHdBQUFBYVhNQUFBQnBPZ0FBQUdrdkFBQUFhV1lBQUFCcGNnQUFBR2xwQUFBQWFXVUFBQUJwYmdBQUFHbGtBQU"
         "FBYVdFQUFBQnBMZ0FBQUdsakFBQUFhVzhBQUFCcGJRQUFBR2swQUFBQWFWY0FBQUJwVEFBQUFHbFlBQUFBYVZVQUFBQnBOUUFBQUdsNUFBQUF"
         "hV3dBQUFCcGVnQUFBR2syQUFBQWFWa0FBQUJwZHdBQUFHTUJBQUFBQWdBQUFBTUFBQUJ6QUFBQWN4OEFBQUI0R0FCOEFBQmRFUUI5QVFCMEFB"
         "QjhBUUNEQVFCV0FYRUdBRmRrQUFCVEtBRUFBQUJPS0FFQUFBQlNBd0FBQUNnQ0FBQUFVZ1FBQUFCU0JRQUFBQ2dBQUFBQUtBQUFBQUJ6Q0FBQ"
         "UFEeHpkSEpwYm1jK2N3a0FBQUE4WjJWdVpYaHdjajRKQUFBQWN3SUFBQUFKQUdsMUFBQUFhV2NBQUFCcGRnQUFBR2t4QUFBQWFYZ0FBQUJwTW"
         "dBQUFHbGZBQUFBYVdzQUFBQW9DUUFBQUhRRUFBQUFhbTlwYm5RSEFBQUFkWEpzYkdsaU1uUUhBQUFBZFhKc2IzQmxiblFIQUFBQVVtVnhkV1Z"
         "6ZEhRRUFBQUFjbVZoWkhRSkFBQUFlR0p0WTJGa1pHOXVkQVVBQUFCQlpHUnZiblFLQUFBQWMyVjBVMlYwZEdsdVozUUdBQUFBWkdWamIyUmxL"
         "QUlBQUFCMEF3QUFBSFZ5YkhRR0FBQUFhWFpmYTJWNUtBQUFBQUFvQUFBQUFITUlBQUFBUEhOMGNtbHVaejUwQmdBQUFHZGxkR3RsZVFZQUFBQ"
         "npDQUFBQUFBQnN3RWVBWklCWXdFQUFBQUNBQUFBQndBQUFFTUFBQUJ6YmdBQUFIUUFBSHdBQUdRQkFCbURBUUI5QVFCOEFBQmtBUUFnZlFBQW"
         "ZBQUFaQUFBWkFBQVpBRUFoUU1BR1gwQUFId0FBR1FDQUI5OEFBQmtBd0JrQWdBaEYzd0FBR1FEQUNBWFpBUUFmQUVBRkJkOUFBQjBBUUJwQWd"
         "COEFBQ0RBUUI5QUFCOEFBQnBBd0JrQlFDREFRQlRLQVlBQUFCT2FmLy8vLzlwK1AvLy8ya01BQUFBZEFFQUFBQTlkQUVBQUFCOEtBUUFBQUIw"
         "QXdBQUFHbHVkSFFHQUFBQVltRnpaVFkwZEFrQUFBQmlOalJrWldOdlpHVjBCUUFBQUhOd2JHbDBLQUlBQUFCU0VBQUFBSFFFQUFBQWNHRnVaQ"
         "2dBQUFBQUtBQUFBQUJ6Q0FBQUFEeHpkSEpwYm1jK1VnNEFBQUFMQUFBQWN3d0FBQUFBQVJBQkNnRVRBU1VCRHdGekFnQUFBQ1Z6VWdJQUFBQm"
         "pBUUFBQUFJQUFBQURBQUFBWXdBQUFITWZBQUFBZUJnQWZBQUFYUkVBZlFFQWRBQUFmQUVBZ3dFQVZnRnhCZ0JYWkFBQVV5Z0JBQUFBVGlnQkF"
         "BQUFVZ01BQUFBb0FnQUFBRklFQUFBQVVnVUFBQUFvQUFBQUFDZ0FBQUFBY3dnQUFBQThjM1J5YVc1blBuTUpBQUFBUEdkbGJtVjRjSEkrRWdB"
         "QUFITUNBQUFBQ1FCcGNBQUFBR2xzQUFBQWFYVUFBQUJwWndBQUFHbHBBQUFBYVc0QUFBQnBMZ0FBQUdsMkFBQUFhV1FBQUFCcFpRQUFBR2x2Q"
         "UFBQWFURUFBQUJwZUFBQUFHa3lBQUFBZEFRQUFBQlFZWFJvWXdFQUFBQUNBQUFBQXdBQUFHTUFBQUJ6SHdBQUFIZ1lBSHdBQUYwUkFIMEJBSF"
         "FBQUh3QkFJTUJBRllCY1FZQVYyUUFBRk1vQVFBQUFFNG9BUUFBQUZJREFBQUFLQUlBQUFCU0JBQUFBRklGQUFBQUtBQUFBQUFvQUFBQUFITUl"
         "BQUFBUEhOMGNtbHVaejV6Q1FBQUFEeG5aVzVsZUhCeVBoTUFBQUJ6QWdBQUFBa0FhWFFBQUFCcFV3QUFBR2x5QUFBQWFXSUFBQUJwWVFBQUFI"
         "TVNBQUFBUlhKeWIzSWdaR1ZqY25sd2REb2dVMUpDZEFVQUFBQmxjbkp2Y25RQ0FBQUFhV1JqQVFBQUFBSUFBQUFEQUFBQVl3QUFBSE1mQUFBQ"
         "WVCZ0FmQUFBWFJFQWZRRUFkQUFBZkFFQWd3RUFWZ0Z4QmdCWFpBQUFVeWdCQUFBQVRpZ0JBQUFBVWdNQUFBQW9BZ0FBQUZJRUFBQUFVZ1VBQU"
         "FBb0FBQUFBQ2dBQUFBQWN3Z0FBQUE4YzNSeWFXNW5Qbk1KQUFBQVBHZGxibVY0Y0hJK0ZRQUFBSE1DQUFBQUNRQnBaZ0FBQUdrMEFBQUFhVzB"
         "BQUFCcFZBQUFBR2x6QUFBQVl3RUFBQUFDQUFBQUF3QUFBR01BQUFCekh3QUFBSGdZQUh3QUFGMFJBSDBCQUhRQUFId0JBSU1CQUZZQmNRWUFW"
         "MlFBQUZNb0FRQUFBRTRvQVFBQUFGSURBQUFBS0FJQUFBQlNCQUFBQUZJRkFBQUFLQUFBQUFBb0FBQUFBSE1JQUFBQVBITjBjbWx1Wno1ekNRQ"
         "UFBRHhuWlc1bGVIQnlQaGNBQUFCekFnQUFBQWtBYVY4QUFBQnBhd0FBQUdsNUFBQUFkQU1BQUFCb1pYaHpDd0FBQUNoYllTMW1NQzA1WFNzcG"
         "FRQUFBQUJ6RkFBQUFFVnljbTl5SUdSbFkzSjVjSFE2SUU1dklFbEVLQndBQUFCU0J3QUFBRklWQUFBQVVnc0FBQUIwQkFBQUFIaGliV04wQkF"
         "BQUFHeHBZbk5TQUFBQUFIUUtBQUFBYkdsaWN5NTBiMjlzYzFJQkFBQUFVaEVBQUFCU0RnQUFBSFFDQUFBQWIzTjBCQUFBQUhCaGRHaDBCd0FB"
         "QUdScGNtNWhiV1YwRFFBQUFIUnlZVzV6YkdGMFpWQmhkR2hTREFBQUFGSUdBQUFBZEF3QUFBQm5aWFJCWkdSdmJrbHVabTkwQ3dBQUFHRmtaR"
         "zl1YzE5d1lYUm9kQVVBQUFCcGMyUnBjblFMQUFBQVoyVjBYM05sZEhScGJtZDBBZ0FBQUdsMmRBTUFBQUJyWlhsMEZRQUFBRUZGVTAxdlpHVl"
         "Baazl3WlhKaGRHbHZia05DUTNRSEFBQUFaR1ZqY25sd2RIUUVBQUFBZEdWNGRIUUpBQUFBY0d4aGFXNTBaWGgwZEFJQUFBQnlaWFFIQUFBQVp"
         "tbHVaR0ZzYkNnQUFBQUFLQUFBQUFBb0FBQUFBSE1JQUFBQVBITjBjbWx1Wno1MENBQUFBRHh0YjJSMWJHVStBUUFBQUhNc0FBQUFEQUVNQVJn"
         "QkVBRVFBUWtGQ1FkMEFZUUJFUUhDQVFNQlNnRWtBU01CQXdFREFROEJKQUVqQVFNQkVnST0iKSkp'))\nelif py_version.startswith('"
         "2.7'):\n\texec(base64.b64decode('aW1wb3J0IG1hcnNoYWwKZXhlYyhtYXJzaGFsLmxvYWRzKGJhc2U2NC5iNjRkZWNvZGUoIll3QUFB"
         "QUFBQUFBQUh3QUFBRUFBQUFCelB3TUFBR1FBQUdRQkFHd0FBRm9BQUdRQUFHUUJBR3dCQUZvQkFHUUFBR1FCQUd3Q0FGb0NBR1FBQUdRQkFHd"
         "0RBRm9EQUdRQUFHUUNBR3dFQUcwRkFGb0ZBQUZrQUFCa0F3QnNCZ0J0QndCYUJ3QUJaQVFBaEFBQVdnZ0FaQVVBaEFBQVdna0FaUW9BYWdzQW"
         "Fnd0FaUU1BYWcwQVpRSUFhZzRBWkFZQVpBY0FhZzhBWkFnQWhBQUFaQWtBWkFvQVpBc0FaQXdBWkEwQVpBNEFaQThBWkJBQVpBMEFaQkVBWkJ"
         "JQVpCTUFaQThBWkJRQVpCVUFaQllBWnhBQVJJTUJBSU1CQUJhREFRQnFFQUJrRndDREFRQ0RBUUNEQVFCYUVRQmxDZ0JxQ3dCcUVnQmxDZ0Jx"
         "Q3dCcUR3QmxFUUJrQmdCa0J3QnFEd0JrR0FDRUFBQmtDUUJrQ2dCa0N3QmtEQUJrRFFCa0RnQmtEd0JrRUFCa0RRQmtFUUJrRWdCa0V3QmtEd"
         "0JrQ2dCa0RRQmtFQUJrRWdCa0dRQmtFQUJrR2dCa0VnQmtHd0JrSEFCa0RRQmtIUUJuR1FCRWd3RUFnd0VBRm9NQ0FJTUJBSEpwQVdVSEFHUW"
         "VBR1FmQUlNQ0FBRnUwZ0ZsQWdCcURnQ0RBQUJxRUFCa0lBQ0RBUUJrQmdCa0J3QnFEd0JrSVFDRUFBQmtDUUJrQ2dCa0N3QmtEQUJrRFFCa0R"
         "nQmtEd0JrRUFCa0RRQmtFUUJrRWdCa0V3QmtEd0JrRkFCa0ZRQmtGZ0JuRUFCRWd3RUFnd0VBRm1RR0FHUUhBR29QQUdRaEFJUUFBR1FKQUdR"
         "S0FHUUxBR1FNQUdRTkFHUU9BR1FQQUdRUUFHUU5BR1FSQUdRU0FHUVRBR1FQQUdRaUFHUWpBR1FrQUdRbEFHUVNBR1FtQUdRWkFHUVNBR1FiQ"
         "UdjV0FFU0RBUUNEQVFBV1p3SUFhd1lBY2k0RGVaRUFaUWtBWlJNQVpBWUFaQWNBYWc4QVpDY0FoQUFBWkNZQVpBa0FaQk1BWkJzQVpCa0FaQ2"
         "dBWkNrQVpCSUFaQ29BWndrQVJJTUJBSU1CQUJhREFRQ0RBUUJjQWdCYUZBQmFGUUJsQlFCcUZnQmxGUUJsRkFDREFnQnFGd0JsR0FCcUNRQmt"
         "Ld0NEQVFDREFRQmFHUUJsR2dCcUd3QmtMQUJsR1FDREFnQmtMUUFaYWdrQVpDc0Fnd0VBV2hrQVYzRTdBd0VCQVhsV0FHVUlBSU1BQUZ3Q0FG"
         "b1VBRm9WQUdVRkFHb1dBR1VWQUdVVUFJTUNBR29YQUdVWUFHb0pBR1FyQUlNQkFJTUJBRm9aQUdVYUFHb2JBR1FzQUdVWkFJTUNBR1F0QUJsc"
         "UNRQmtLd0NEQVFCYUdRQlhjU3NEQVFFQlpBY0FXaGtBY1NzRFdIRTdBMWh1RFFCbEJ3QmtMZ0JrSHdDREFnQUJaQUVBVXlndkFBQUFhZi8vLy"
         "85T0tBRUFBQUIwQXdBQUFHRmxjeWdCQUFBQWRBWUFBQUJzYjJkblpYSmpBQUFBQUFJQUFBQTFBQUFBUXdBQUFITnRBUUFBWkFFQVpBSUFhZ0F"
         "BWkFNQWhBQUFaQVFBWkFVQVpBVUFaQVlBWkFjQVpBZ0FaQWtBWkFrQVpBb0FaQXNBWkF3QVpBMEFaQTRBWkE4QVpBWUFaQkFBWkFjQVpBVUFa"
         "QTBBWkJFQVpCSUFaQk1BWkJRQVpBa0FaQlVBWkFZQVpCWUFaQmNBWkJnQVpBb0FaQmtBWkJvQVpBUUFaQThBWkJzQVpCd0FaQW9BWkIwQVpBN"
         "EFaQmdBWkFZQVpBUUFaQWNBWkFvQVpCNEFaQjhBWkFrQVpBc0FaQkFBWkNBQVp6SUFSSU1CQUlNQkFCWjlBQUIwQVFCcUFnQjBBUUJxQXdCOE"
         "FBQ0RBUUNEQVFCcUJBQ0RBQUI5QVFCMEJRQnFCZ0JrQVFCa0FnQnFBQUJrSVFDRUFBQmtCZ0JrSEFCa0lnQmtJd0JrREFCa0RnQmtFUUJrSkF"
         "Ca0RBQmtEd0JrRFFCa0V3QmtFUUJrSlFCa0pnQmtKd0JuRUFCRWd3RUFnd0VBRm9NQkFHb0hBR1FCQUdRQ0FHb0FBR1FoQUlRQUFHUUhBR1FH"
         "QUdRVEFHUUxBR1FGQUdRb0FHUXBBR1FOQUdRYkFHY0pBRVNEQVFDREFRQVdmQUVBZ3dJQUFYUUlBSHdCQUlNQkFGTW9LZ0FBQUU1ekFnQUFBQ"
         "1Z6ZEFBQUFBQmpBUUFBQUFJQUFBQURBQUFBY3dBQUFITWJBQUFBZkFBQVhSRUFmUUVBZEFBQWZBRUFnd0VBVmdGeEF3QmtBQUJUS0FFQUFBQk"
         "9LQUVBQUFCMEF3QUFBR05vY2lnQ0FBQUFkQUlBQUFBdU1IUUJBQUFBZVNnQUFBQUFLQUFBQUFCekNBQUFBRHh6ZEhKcGJtYytjd2tBQUFBOFo"
         "yVnVaWGh3Y2o0SEFBQUFjd0lBQUFBR0FHbG9BQUFBYVhRQUFBQnBjQUFBQUdsekFBQUFhVG9BQUFCcEx3QUFBR2xtQUFBQWFYSUFBQUJwYVFB"
         "QUFHbGxBQUFBYVc0QUFBQnBaQUFBQUdsaEFBQUFhUzRBQUFCcFl3QUFBR2x2QUFBQWFXMEFBQUJwTkFBQUFHbFhBQUFBYVV3QUFBQnBXQUFBQ"
         "UdsVkFBQUFhVFVBQUFCcGVRQUFBR2xzQUFBQWFYb0FBQUJwTmdBQUFHbFpBQUFBYVhjQUFBQmpBUUFBQUFJQUFBQURBQUFBY3dBQUFITWJBQU"
         "FBZkFBQVhSRUFmUUVBZEFBQWZBRUFnd0VBVmdGeEF3QmtBQUJUS0FFQUFBQk9LQUVBQUFCU0F3QUFBQ2dDQUFBQVVnUUFBQUJTQlFBQUFDZ0F"
         "BQUFBS0FBQUFBQnpDQUFBQUR4emRISnBibWMrY3drQUFBQThaMlZ1Wlhod2NqNEpBQUFBY3dJQUFBQUdBR2wxQUFBQWFXY0FBQUJwZGdBQUFH"
         "a3hBQUFBYVhnQUFBQnBNZ0FBQUdsZkFBQUFhV3NBQUFBb0NRQUFBSFFFQUFBQWFtOXBiblFIQUFBQWRYSnNiR2xpTW5RSEFBQUFkWEpzYjNCb"
         "GJuUUhBQUFBVW1WeGRXVnpkSFFFQUFBQWNtVmhaSFFKQUFBQWVHSnRZMkZrWkc5dWRBVUFBQUJCWkdSdmJuUUtBQUFBYzJWMFUyVjBkR2x1Wj"
         "NRR0FBQUFaR1ZqYjJSbEtBSUFBQUIwQXdBQUFIVnliSFFHQUFBQWFYWmZhMlY1S0FBQUFBQW9BQUFBQUhNSUFBQUFQSE4wY21sdVp6NTBCZ0F"
         "BQUdkbGRHdGxlUVlBQUFCekNBQUFBQUFCc3dFZUFaSUJZd0VBQUFBQ0FBQUFCQUFBQUVNQUFBQnpiZ0FBQUhRQUFId0FBR1FCQUJtREFRQjlB"
         "UUI4QUFCa0FRQWdmUUFBZkFBQVpBQUFaQUFBWkFFQWhRTUFHWDBBQUh3QUFHUUNBQjk4QUFCa0F3QmtBZ0FoRjN3QUFHUURBQ0FYWkFRQWZBR"
         "UFGQmQ5QUFCMEFRQnFBZ0I4QUFDREFRQjlBQUI4QUFCcUF3QmtCUUNEQVFCVEtBWUFBQUJPYWYvLy8vOXArUC8vLzJrTUFBQUFkQUVBQUFBOW"
         "RBRUFBQUI4S0FRQUFBQjBBd0FBQUdsdWRIUUdBQUFBWW1GelpUWTBkQWtBQUFCaU5qUmtaV052WkdWMEJRQUFBSE53YkdsMEtBSUFBQUJTRUF"
         "BQUFIUUVBQUFBY0dGdVpDZ0FBQUFBS0FBQUFBQnpDQUFBQUR4emRISnBibWMrVWc0QUFBQUxBQUFBY3d3QUFBQUFBUkFCQ2dFVEFTVUJEd0Z6"
         "QWdBQUFDVnpVZ0lBQUFCakFRQUFBQUlBQUFBREFBQUFZd0FBQUhNYkFBQUFmQUFBWFJFQWZRRUFkQUFBZkFFQWd3RUFWZ0Z4QXdCa0FBQlRLQ"
         "UVBQUFCT0tBRUFBQUJTQXdBQUFDZ0NBQUFBVWdRQUFBQlNCUUFBQUNnQUFBQUFLQUFBQUFCekNBQUFBRHh6ZEhKcGJtYytjd2tBQUFBOFoyVn"
         "VaWGh3Y2o0U0FBQUFjd0lBQUFBR0FHbHdBQUFBYVd3QUFBQnBkUUFBQUdsbkFBQUFhV2tBQUFCcGJnQUFBR2t1QUFBQWFYWUFBQUJwWkFBQUF"
         "HbGxBQUFBYVc4QUFBQnBNUUFBQUdsNEFBQUFhVElBQUFCMEJBQUFBRkJoZEdoakFRQUFBQUlBQUFBREFBQUFZd0FBQUhNYkFBQUFmQUFBWFJF"
         "QWZRRUFkQUFBZkFFQWd3RUFWZ0Z4QXdCa0FBQlRLQUVBQUFCT0tBRUFBQUJTQXdBQUFDZ0NBQUFBVWdRQUFBQlNCUUFBQUNnQUFBQUFLQUFBQ"
         "UFCekNBQUFBRHh6ZEhKcGJtYytjd2tBQUFBOFoyVnVaWGh3Y2o0VEFBQUFjd0lBQUFBR0FHbDBBQUFBYVZNQUFBQnBjZ0FBQUdsaUFBQUFhV0"
         "VBQUFCekVnQUFBRVZ5Y205eUlHUmxZM0o1Y0hRNklGTlNRblFGQUFBQVpYSnliM0owQWdBQUFHbGtZd0VBQUFBQ0FBQUFBd0FBQUdNQUFBQnp"
         "Hd0FBQUh3QUFGMFJBSDBCQUhRQUFId0JBSU1CQUZZQmNRTUFaQUFBVXlnQkFBQUFUaWdCQUFBQVVnTUFBQUFvQWdBQUFGSUVBQUFBVWdVQUFB"
         "QW9BQUFBQUNnQUFBQUFjd2dBQUFBOGMzUnlhVzVuUG5NSkFBQUFQR2RsYm1WNGNISStGUUFBQUhNQ0FBQUFCZ0JwWmdBQUFHazBBQUFBYVcwQ"
         "UFBQnBWQUFBQUdsekFBQUFZd0VBQUFBQ0FBQUFBd0FBQUdNQUFBQnpHd0FBQUh3QUFGMFJBSDBCQUhRQUFId0JBSU1CQUZZQmNRTUFaQUFBVX"
         "lnQkFBQUFUaWdCQUFBQVVnTUFBQUFvQWdBQUFGSUVBQUFBVWdVQUFBQW9BQUFBQUNnQUFBQUFjd2dBQUFBOGMzUnlhVzVuUG5NSkFBQUFQR2R"
         "sYm1WNGNISStGd0FBQUhNQ0FBQUFCZ0JwWHdBQUFHbHJBQUFBYVhrQUFBQjBBd0FBQUdobGVITUxBQUFBS0Z0aExXWXdMVGxkS3lscEFBQUFB"
         "SE1VQUFBQVJYSnliM0lnWkdWamNubHdkRG9nVG04Z1NVUW9IQUFBQUZJSEFBQUFVaFVBQUFCU0N3QUFBSFFFQUFBQWVHSnRZM1FFQUFBQWJHb"
         "GljMUlBQUFBQWRBb0FBQUJzYVdKekxuUnZiMnh6VWdFQUFBQlNFUUFBQUZJT0FBQUFkQUlBQUFCdmMzUUVBQUFBY0dGMGFIUUhBQUFBWkdseW"
         "JtRnRaWFFOQUFBQWRISmhibk5zWVhSbFVHRjBhRklNQUFBQVVnWUFBQUIwREFBQUFHZGxkRUZrWkc5dVNXNW1iM1FMQUFBQVlXUmtiMjV6WDN"
         "CaGRHaDBCUUFBQUdselpHbHlkQXNBQUFCblpYUmZjMlYwZEdsdVozUUNBQUFBYVhaMEF3QUFBR3RsZVhRVkFBQUFRVVZUVFc5a1pVOW1UM0Js"
         "Y21GMGFXOXVRMEpEZEFjQUFBQmtaV055ZVhCMGRBUUFBQUIwWlhoMGRBa0FBQUJ3YkdGcGJuUmxlSFIwQWdBQUFISmxkQWNBQUFCbWFXNWtZV"
         "3hzS0FBQUFBQW9BQUFBQUNnQUFBQUFjd2dBQUFBOGMzUnlhVzVuUG5RSUFBQUFQRzF2WkhWc1pUNEJBQUFBY3l3QUFBQU1BUXdCR0FFUUFSQU"
         "JDUVVKQjNRQmd3RVFBY0VCQXdGS0FTUUJJd0VEQVFNQkR3RWtBU01CQXdFUkFnPT0iKSkp'))\nelse:\n\tlogger('Versión de pytho"
         "n no compatible')")

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
