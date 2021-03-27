# -*- coding: utf-8 -*-

import os, re

from platformcode import config, logger, platformtools
from core import httptools, scrapertools, jsontools


channels_poe = [
        ['documaniatv', 'https://www.documaniatv.com/'],
        ['gdrive', 'https://drive.google.com/drive/'],
        ['playdede', 'https://playdede.com']
        ]

servers_poe = [
        ['directo'],
        ['m3u8hls'],
        ['mystream'],
        ['torrent']
        ]


def test_channel(channel_name):
    logger.info()

    channel_id = channel_name.lower()

    channel_json = channel_id + '.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    try:
       with open(filename_json, 'r') as f: data = f.read(); f.close()
       params = jsontools.load(data)
    except:
       platformtools.dialog_notification(config.__addon_name, 'Falta [COLOR red]' + channel_json + '[/COLOR]')
       return

    if params['active'] == False:
        platformtools.dialog_notification(config.__addon_name, '[COLOR blue]' + channel_name + '[COLOR red] inactivo [/COLOR]')
        return

    txt = test_internet()

    txt += '[COLOR moccasin][B]Parámetros:[/B][/COLOR][CR]'
    txt += 'id: ' + str(params['id']) + '[CR]'
    txt += 'searchable: ' + str(params['searchable']) + '[CR]'
    txt += 'search_types: ' + str(params['search_types']) + '[CR]'
    txt += 'categories: ' + str(params['categories']) + '[CR]'
    txt += 'language: ' + str(params['language']) + '[CR]'
    txt += 'clusters: ' + str(params['clusters']) + '[CR]'
    txt += 'notes: ' + str(params['notes'])

    channel_py = channel_id + '.py'
    filename_py = os.path.join(config.get_runtime_path(), 'channels', channel_py)

    dominio = ''

    channel_poe = "'" + channel_id + "'"
    esta_en_poe = False

    if channel_poe in str(channels_poe):
        for x in channels_poe:
            if x[0] == channel_id:
               esta_en_poe = True
               channel_poe = x[0]
               host = x[1]
               break

    if not esta_en_poe:
       channel_poe = ''

       try:
          with open(filename_py, 'r') as f: data = f.read(); f.close()
       except:
          platformtools.dialog_notification(config.__addon_name, 'Falta [COLOR red]' + channel_py + '[/COLOR]')
          return

       part_py = 'mainlist'
       if 'configurar_proxies' in data: part_py = 'configurar_proxies'
       elif 'do_downloadpage' in data: part_py = 'do_downloadpage'

       bloc = scrapertools.find_single_match(data.lower(), '(.*?)' + part_py)
       bloc = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', bloc)

       host = scrapertools.find_single_match(bloc, 'host.*?"(.*?)"')
       if not host:
           host = scrapertools.find_single_match(bloc, "host.*?'(.*?)'")

    host = host.strip()

    if not host:
        dominio = config.get_setting('dominio', channel_id, default='')
        if dominio:
            host = dominio
        else:
            platformtools.dialog_notification(config.__addon_name, 'Falta host [COLOR red]' + channel_py + '[/COLOR]')
            return

    txt = info_channel(channel_name, channel_poe, host, dominio, txt)

    platformtools.dialog_textviewer(channel_name, txt)


def info_channel(channel_name, channel_poe, host, dominio, txt):
    platformtools.dialog_notification(config.__addon_name, 'Accediendo [COLOR blue]' + channel_name + '[/COLOR]')

    channel_id = channel_name.lower()

    if dominio:
       txt_dominio = 'dominio'
    else:
       txt_dominio = ''

    response, txt = acces_channel(channel_name, host, txt_dominio, txt, follow_redirects=False)

    if channel_id == channel_poe:
        return txt

    if response.sucess == False:
        response = acces_channel(channel_name, host, '', txt, follow_redirects=True)

    if not dominio:
        dominio = config.get_setting('dominio', channel_id, default='')
        if dominio:
            response, txt = acces_channel(channel_name, dominio, 'dominio', txt, follow_redirects=False)

    return txt


def acces_channel(channel_name, host, dominio, txt, follow_redirects=True):
    platformtools.dialog_notification(config.__addon_name, 'Testeando [COLOR moccasin]' + channel_name + '[/COLOR]')

    channel_id = channel_name.lower()

    text_with_proxies = ''

    cfg_proxies_channel = 'channel_' + channel_id + '_proxies'
    if not config.get_setting(cfg_proxies_channel, default=''):
        response = httptools.downloadpage(host, follow_redirects=follow_redirects, raise_weberror=False)
    else:
        response = httptools.downloadpage_proxy(channel_id, host, follow_redirects=follow_redirects, raise_weberror=False)
        text_with_proxies = '[COLOR red] con proxies [/COLOR]'

    if dominio:
        dominio = '[COLOR coral]' + dominio + '[/COLOR]'

    if follow_redirects == False:
        txt += '[CR][CR]'
        txt += '[COLOR moccasin][B]Acceso: ' + dominio + ' ' + text_with_proxies + '[/B][/COLOR][CR]'
        txt += 'host: ' + host + '[CR]'
    else:
        txt += '[CR][CR]'
        txt += '[COLOR moccasin][B]Acceso Redirect: ' + dominio + ' ' + text_with_proxies + '[/B][/COLOR][CR]'
        txt += 'host: ' + host + '[CR]'

    if response.sucess == True:
        color_sucess = '[COLOR yellow][B]'
    else:
        color_sucess = '[COLOR red][B]'

    txt += 'sucess: ' + color_sucess + str(response.sucess) + '[/B][/COLOR][CR]'

    txt += 'code: ' + str(response.code) + '[CR]'
    txt += 'error: ' + str(response.error) + '[CR]'
    txt += 'data length: ' + str(len(response.data))

    if response.sucess == True:
        if len(response.data) < 1000:
            txt += '[CR][CR]'
            txt += '[COLOR moccasin][B]Headers:[/B][/COLOR][CR]'
            txt += str(response.headers) + '[CR]'

            if len(response.data) > 0:
                txt += '[CR][CR]'
                txt += '[COLOR moccasin][B]Data:[/B][/COLOR][CR]'
                txt += str(response.data) + '[CR]'

    return response, txt


def test_server(server_name):
    logger.info()

    server_id = server_name.lower()

    server_json = server_id + '.json'
    filename_json = os.path.join(config.get_runtime_path(), 'servers', server_json)

    try:
       with open(filename_json, 'r') as f: data = f.read(); f.close()
       dict_server = jsontools.load(data)
    except:
       platformtools.dialog_notification(config.__addon_name, 'Falta [COLOR red]' + server_json + '[/COLOR]')
       return

    if dict_server['active'] == False:
        platformtools.dialog_notification(config.__addon_name, '[COLOR blue]' + server_name + '[COLOR red] inactivo [/COLOR]')
        return

    if 'find_videos' in dict_server:
        dict_server['find_videos']['patterns'] = dict_server['find_videos'].get('patterns', list())
    else:
        platformtools.dialog_notification(config.__addon_name, '[COLOR blue]' + server_name + 'Falta [COLOR red] find_videos [/COLOR]')
        return

    txt = test_internet()

    bloc = str(dict_server['find_videos']['patterns'])

    servers = scrapertools.find_multiple_matches(str(bloc), '.*?"url".*?"(.*?)"')
    if not servers:
        servers = scrapertools.find_multiple_matches(str(bloc), ".*?'url'.*?'(.*?)'")

    if not servers:
        platformtools.dialog_notification(config.__addon_name, 'Falta url [COLOR red]' + server_name + '[/COLOR]')
        return

    url_servidor = ''

    server_poe = "'" + server_id + "'"
    esta_en_poe = False

    for url in servers:
        if server_poe in str(servers_poe):
           for x in servers_poe:
               if x[0] == server_id:
                  esta_en_poe = True
                  server_poe = x[0]
                  url_servidor = server_id
                  break

        if not esta_en_poe:
           server_poe = ''

           try:
              type = url.split('/')[0].strip()
              servidor = url.split('/')[2].strip()

              if type:
                  if servidor:
                      url_servidor = type + '//' + servidor + '/'
           except:
              url_servidor = url

        continue

    txt += '[COLOR moccasin][B]Parámetros:[/B][/COLOR][CR]'
    txt += 'patterns: ' + str(bloc) + '[CR][CR]'

    if url_servidor == '':
        url_servidor = 'Indefinido'
    elif '\\' in url_servidor:
        url_servidor = 'Variable'

    if not url_servidor:
       txt += 'url: [COLOR red][B] Falta [/B][/COLOR][CR]'
    else:
       txt += 'url: ' + url_servidor
       txt = info_server(server_name, server_poe, url_servidor, txt)

    platformtools.dialog_textviewer(server_name, txt)


def info_server(server_name, server_poe, url, txt):
    platformtools.dialog_notification(config.__addon_name, 'Accediendo [COLOR blue]' + server_name + '[/COLOR]')

    server_id = server_name.lower()

    if server_id == server_poe:
        return txt
    elif url == 'Indefinido':
        return txt
    elif url == 'Variable':
        return txt

    response, txt = acces_server(server_name, url, txt, follow_redirects=False)

    if response.sucess == False:
        response = acces_server(server_name, url, txt, follow_redirects=True)

    return txt

def acces_server(server_name, url, txt, follow_redirects=True):
    platformtools.dialog_notification(config.__addon_name, 'Testeando [COLOR moccasin]' + server_name + '[/COLOR]')

    server_id = server_name.lower()

    text_with_proxies = ''

    response = httptools.downloadpage(url, follow_redirects=follow_redirects, raise_weberror=False)

    if follow_redirects == False:
        txt += '[CR][CR]'
        txt += '[COLOR moccasin][B]Acceso: [/B][/COLOR][CR]'
        txt += 'host: ' + url + '[CR]'
    else:
        txt += '[CR][CR]'
        txt += '[COLOR moccasin][B]Acceso Redirect: [/B][/COLOR][CR]'
        txt += 'host: ' + url + '[CR]'

    if response.sucess == True:
        color_sucess = '[COLOR yellow][B]'
    else:
        color_sucess = '[COLOR red][B]'

    txt += 'sucess: ' + color_sucess + str(response.sucess) + '[/B][/COLOR][CR]'

    txt += 'code: ' + str(response.code) + '[CR]'
    txt += 'error: ' + str(response.error) + '[CR]'
    txt += 'data length: ' + str(len(response.data))

    if response.sucess == True:
        if len(response.data) < 100:
            txt += '[CR][CR]'
            txt += '[COLOR moccasin][B]Headers:[/B][/COLOR][CR]'
            txt += str(response.headers) + '[CR]'

            if len(response.data) > 0:
                txt += '[CR][CR]'
                txt += '[COLOR moccasin][B]Data:[/B][/COLOR][CR]'
                txt += str(response.data) + '[CR]'

    return response, txt


def test_internet():
    platformtools.dialog_notification(config.__addon_name, 'Comprobando [COLOR blue]Internet[/COLOR]')

    hay_internet = True
    your_ip = ''

    try:
       data = httptools.downloadpage('http://httpbin.org/ip').data
       if len(data) == 0: hay_internet = False
       else:
          your_ip = scrapertools.find_single_match(data, 'origin".*?"(.*?)"')
          if not your_ip: hay_internet = False
    except:
       hay_internet = False
       your_ip = '[COLOR blue]No se ha podido comprobar[/COLOR]'

    if not hay_internet:
	    platformtools.dialog_ok(config.__addon_name, '[COLOR red]Parece que NO hay conexión con internet.[/COLOR]', 'Compruebelo realizando cualquier Búsqueda, desde un Navegador Web ')

    if not hay_internet: 
        if your_ip == '': your_ip = '[COLOR red] Sin Conexión [/COLOR]'

    txt = '[COLOR moccasin][B]Internet:[/B][/COLOR]  %s ' % your_ip
    txt += '[CR][CR]'

    return txt