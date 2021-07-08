# -*- coding: utf-8 -*-

import xbmcgui

from platformcode import config, logger, platformtools
from core.item import Item
from core import channeltools, scrapertools

color_list_prefe = config.get_setting('channels_list_prefe_color', default='gold')
color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')
color_list_inactive = config.get_setting('channels_list_inactive_color', default='gray')

color_alert = config.get_setting('notification_alert_color', default='red')
color_infor = config.get_setting('notification_infor_color', default='pink')
color_adver = config.get_setting('notification_adver_color', default='violet')
color_avis  = config.get_setting('notification_avis_color', default='yellow')
color_exec  = config.get_setting('notification_exec_color', default='cyan')

cfg_search_excluded_movies = 'search_excludes_movies'
cfg_search_excluded_tvshows = 'search_excludes_tvshows'
cfg_search_excluded_documentaries = 'search_excludes_documentaries'
cfg_search_excluded_mixed = 'search_excludes_mixed'
cfg_search_excluded_all = 'search_excludes_all'

channels_search_excluded_movies = config.get_setting(cfg_search_excluded_movies, default='')
channels_search_excluded_tvshows = config.get_setting(cfg_search_excluded_tvshows, default='')
channels_search_excluded_documentaries = config.get_setting(cfg_search_excluded_documentaries, default='')
channels_search_excluded_mixed = config.get_setting(cfg_search_excluded_mixed, default='')
channels_search_excluded_all = config.get_setting(cfg_search_excluded_all, default='')


def mainlist(item):
    logger.info()
    itemlist = []

    tot_opt_anular = 0

    if config.get_setting('channels_link_main', default=True):
        if channels_search_excluded_mixed: tot_opt_anular += 1

    if channels_search_excluded_movies: tot_opt_anular += 1

    if channels_search_excluded_tvshows: tot_opt_anular += 1

    if channels_search_excluded_documentaries: tot_opt_anular += 1

    if config.get_setting('channels_link_main', default=True):
        itemlist.append(item.clone( action = 'channels_excluded', title='Excluir canales en las búsquedas de Películas y/o Series', extra = 'mixed', folder = False ))

    itemlist.append(item.clone( action = 'channels_excluded', title='Excluir canales en las búsquedas de Películas', extra = 'movies', folder = False ))
    itemlist.append(item.clone( action = 'channels_excluded', title='Excluir canales en las búsquedas de Series', extra = 'tvshows', folder = False ))
    itemlist.append(item.clone( action = 'channels_excluded', title='Excluir canales en las búsquedas de Documentales', extra = 'documentaries', folder = False ))

    if config.get_setting('channels_link_main', default=True):
        itemlist.append(item.clone( action = 'channels_excluded', title='Excluir canales en las búsquedas de Películas, Series y Documentales', extra = 'all', folder = False ))

    if config.get_setting('channels_link_main', default=True):
        if channels_search_excluded_mixed:
            itemlist.append(item.clone( title = 'Anular las exclusiones para Películas y/o Series', action = 'channels_excluded_del', extra = 'mixed', folder = False, text_color='coral' ))

    if channels_search_excluded_movies:
        itemlist.append(item.clone( title = 'Anular las exclusiones para Películas', action = 'channels_excluded_del', extra = 'movies', folder = False, text_color='coral' ))

    if channels_search_excluded_tvshows:
        itemlist.append(item.clone( title = 'Anular las exclusiones para Series', action = 'channels_excluded_del', extra = 'tvshows', folder = False, text_color='coral' ))

    if channels_search_excluded_documentaries:
        itemlist.append(item.clone( title = 'Anular las exclusiones para Documentales', action = 'channels_excluded_del', extra = 'documentaries', folder = False, text_color='coral' ))

    if config.get_setting('channels_link_main', default=True):
        if channels_search_excluded_all or tot_opt_anular > 1:
            itemlist.append(item.clone( title = 'Anular todas las exclusiones', action = 'channels_excluded_del', extra= 'all', folder = False, text_color='yellow' ))

    return itemlist


def only_animes(item):
    logger.info()

    descartar_anime = config.get_setting('descartar_anime', default=False)

    if descartar_anime: return

    cabecera = 'Canales con contenido de Animes'
    filtros = {'clusters': 'anime'}

    opciones_channels = []
    canales_animes = []

    ch_list = channeltools.get_channels_list(filtros=filtros)

    if not ch_list:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin canales de este tipo[/B][/COLOR]' % color_adver)
        return

    for ch in ch_list:
        info = ''

        if ch['status'] == 1:
            info = info + '[B][COLOR %s][I] Preferido [/I][/B][/COLOR]' % color_list_prefe
        elif ch['status'] == -1:
            info = info + '[B][COLOR %s][I] Desactivado [/I][/B][/COLOR]' % color_list_inactive

        if 'dominios' in ch['notes'].lower():
            dominio = config.get_setting('channel_' + ch['id'] + '_dominio', default='')
            if dominio:
                dominio = dominio.replace('https://', '').replace('/', '')
                info = info + '[B][COLOR cyan] %s [/B][/COLOR]' % dominio

        cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'
        if config.get_setting(cfg_proxies_channel, default=''):
            info = info + '[B][COLOR %s] Proxies [/B][/COLOR]' % color_list_proxies

        tipos = ch['search_types']
        tipos = str(tipos).replace('[', '').replace(']', '').replace("'", '')

        if ch['searchable'] == False:
            tipos = str(tipos).replace('movie', 'Vídeos')
            tipos = str(tipos).replace('movie', 'Películas').replace('tvshow', 'Series')
        else:
            tipos = str(tipos).replace('movie', 'Películas').replace('tvshow', 'Series').replace('documentary', 'Documentales').replace('all,', '')

        if info: info = info + '  '
        info = info + '[COLOR mediumspringgreen][B]' + tipos + '[/B][/COLOR]'

        idiomas = ch['language']
        idiomas = str(idiomas).replace('[', '').replace(']', '').replace("'", '')
        idiomas = str(idiomas).replace('cast', 'Esp').replace('lat', 'Lat').replace('vose', 'Vose')

        if info: info = info + '  '
        info = info + '[COLOR mediumaquamarine]' + idiomas + '[/COLOR]'

        channel_name = ch['name']
        channel_thumb = ch['thumbnail']

        opciones_channels.append(platformtools.listitem_to_select('[COLOR yellow]' + channel_name + '[/COLOR]', info, channel_thumb))

        canales_animes.append((ch['name'], info, ch['notes']))

    ret = platformtools.dialog_select(cabecera, opciones_channels, useDetails=True)

    if not ret == -1:
        canal = canales_animes[ret]
        tests_channels(canal[0], canal[1], canal[2])


def only_adults(item):
    logger.info()

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    if descartar_xxx: return

    cabecera = 'Canales con contenido para Adultos'
    filtros = {'clusters': 'adults'}

    opciones_channels = []
    canales_adults = []

    ch_list = channeltools.get_channels_list(filtros=filtros)

    if not ch_list:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin canales de este tipo[/B][/COLOR]' % color_adver)
        return

    for ch in ch_list:
        info = ''

        if ch['status'] == 1:
            info = info + '[B][COLOR %s][I] Preferido [/I][/B][/COLOR]' % color_list_prefe
        elif ch['status'] == -1:
            info = info + '[B][COLOR %s][I] Desactivado [/I][/B][/COLOR]' % color_list_inactive

        if 'dominios' in ch['notes'].lower():
            dominio = config.get_setting('channel_' + ch['id'] + '_dominio', default='')
            if dominio:
                dominio = dominio.replace('https://', '').replace('/', '')
                info = info + '[B][COLOR cyan] %s [/B][/COLOR]' % dominio

        cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'
        if config.get_setting(cfg_proxies_channel, default=''):
            info = info + '[B][COLOR %s] Proxies [/B][/COLOR]' % color_list_proxies

        tipos = ch['search_types']
        tipos = str(tipos).replace('[', '').replace(']', '').replace("'", '')

        if ch['searchable'] == False:
            tipos = str(tipos).replace('movie', 'Vídeos')
        else:
            tipos = str(tipos).replace('movie', 'Películas').replace('tvshow', 'Series').replace('documentary', 'Documentales').replace('all,', '')

        if info: info = info + '  '
        info = info + '[COLOR mediumspringgreen][B]' + tipos + '[/B][/COLOR]'

        idiomas = ch['language']
        idiomas = str(idiomas).replace('[', '').replace(']', '').replace("'", '')
        idiomas = str(idiomas).replace('cast', 'Esp').replace('lat', 'Lat').replace('vose', 'Vose')

        if info: info = info + '  '
        info = info + '[COLOR mediumaquamarine]' + idiomas + '[/COLOR]'

        channel_name = ch['name']
        channel_thumb = ch['thumbnail']

        opciones_channels.append(platformtools.listitem_to_select('[COLOR yellow]' + channel_name + '[/COLOR]', info, channel_thumb))

        canales_adults.append((ch['name'], info, ch['notes']))

    ret = platformtools.dialog_select(cabecera, opciones_channels, useDetails=True)

    if not ret == -1:
        canal = canales_adults[ret]
        tests_channels(canal[0], canal[1], canal[2])


def with_proxies(item):
    logger.info()

    no_proxies = config.get_setting('search_no_proxies', default=False)

    cabecera = 'Canales que pueden necesitar Proxies'
    filtros = {'searchable': True}

    opciones_channels = []
    canales_proxies = []

    ch_list = channeltools.get_channels_list(filtros=filtros)

    i = 0
    for ch in ch_list:
        if not 'proxies' in ch['notes'].lower():
            continue

        i =+1

    if i == 0:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin canales con proxies memorizados[/B][/COLOR]' % color_adver)
        return

    for ch in ch_list:
        if not 'proxies' in ch['notes'].lower():
            continue

        cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'
        cfg_proxytools_max_channel = 'channel_' + ch['id'] + '_proxytools_max'
        cfg_proxytools_provider = 'channel_' + ch['id'] + '_proxytools_provider'

        info = ''

        if ch['status'] == 1:
            info = info + '[B][COLOR %s][I] Preferido [/I][/B][/COLOR]' % color_list_prefe
        elif ch['status'] == -1:
            info = info + '[B][COLOR %s][I] Desactivado [/I][/B][/COLOR]' % color_list_inactive

        if 'dominios' in ch['notes'].lower():
            dominio = config.get_setting('channel_' + ch['id'] + '_dominio', default='')
            if dominio:
                dominio = dominio.replace('https://', '').replace('/', '')
                info = info + '[B][COLOR cyan] %s [/B][/COLOR]' % dominio

        if config.get_setting(cfg_proxies_channel, default=''):
            info = info + '[B][COLOR %s] Proxies [/B][/COLOR]' % color_list_proxies
        elif config.get_setting(cfg_proxytools_max_channel, default=''):
            info = info + '[COLOR yellowgreen][B] Sin proxies [/B][/COLOR]'
        elif config.get_setting(cfg_proxytools_provider, default=''):
            info = info + '[COLOR yellowgreen][B] Sin proxies [/B][/COLOR]'

        if no_proxies:
            info = info + '[COLOR white][B] EXCLUIDO Buscar [/B][/COLOR]'

        tipos = ch['search_types']
        tipos = str(tipos).replace('[', '').replace(']', '').replace("'", '')
        tipos = str(tipos).replace('movie', 'Películas').replace('tvshow', 'Series').replace('documentary', 'Documentales').replace('all,', '')

        if info: info = info + '  '
        info = info + '[COLOR mediumspringgreen][B]' + tipos + '[/B][/COLOR]'

        idiomas = ch['language']
        idiomas = str(idiomas).replace('[', '').replace(']', '').replace("'", '')
        idiomas = str(idiomas).replace('cast', 'Esp').replace('lat', 'Lat').replace('vose', 'Vose')

        if info: info = info + '  '
        info = info + '[COLOR mediumaquamarine]' + idiomas + '[/COLOR]'

        channel_name = ch['name']
        channel_thumb = ch['thumbnail']

        opciones_channels.append(platformtools.listitem_to_select('[COLOR yellow]' + channel_name + '[/COLOR]', info, channel_thumb))

        canales_proxies.append((ch['name'], info, ch['notes']))

    ret = platformtools.dialog_select(cabecera, opciones_channels, useDetails=True)

    if not ret == -1:
        canal = canales_proxies[ret]
        tests_channels(canal[0], canal[1], canal[2])


def no_actives(item):
    logger.info()

    cabecera = 'Canales Desactivados'
    filtros = {'searchable': True}

    opciones_channels = []
    canales_no_actives = []

    ch_list = channeltools.get_channels_list(filtros=filtros)

    i = 0
    for ch in ch_list:
        if not ch['status'] == -1:
            continue

        i =+1

    if i == 0:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin canales desactivados[/B][/COLOR]' % color_adver)
        return

    for ch in ch_list:
        if not ch['status'] == -1:
            continue

        cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'
        cfg_proxytools_max_channel = 'channel_' + ch['id'] + '_proxytools_max'
        cfg_proxytools_provider = 'channel_' + ch['id'] + '_proxytools_provider'

        info = ''

        info = info + '[B][COLOR %s][I] Desactivado [/I][/B][/COLOR]' % color_list_inactive

        if 'dominios' in ch['notes'].lower():
            dominio = config.get_setting('channel_' + ch['id'] + '_dominio', default='')
            if dominio:
                dominio = dominio.replace('https://', '').replace('/', '')
                info = info + '[B][COLOR cyan] %s [/B][/COLOR]' % dominio

        if config.get_setting(cfg_proxies_channel, default=''):
            info = info + '[B][COLOR %s] Proxies [/B][/COLOR]' % color_list_proxies
        elif config.get_setting(cfg_proxytools_max_channel, default=''):
            info = info + '[COLOR yellowgreen][B] Sin proxies [/B][/COLOR]'
        elif config.get_setting(cfg_proxytools_provider, default=''):
            info = info + '[COLOR yellowgreen][B] Sin proxies [/B][/COLOR]'

        tipos = ch['search_types']
        tipos = str(tipos).replace('[', '').replace(']', '').replace("'", '')
        tipos = str(tipos).replace('movie', 'Películas').replace('tvshow', 'Series').replace('documentary', 'Documentales').replace('all,', '')

        if info: info = info + '  '
        info = info + '[COLOR mediumspringgreen][B]' + tipos + '[/B][/COLOR]'

        idiomas = ch['language']
        idiomas = str(idiomas).replace('[', '').replace(']', '').replace("'", '')
        idiomas = str(idiomas).replace('cast', 'Esp').replace('lat', 'Lat').replace('vose', 'Vose')

        if info: info = info + '  '
        info = info + '[COLOR mediumaquamarine]' + idiomas + '[/COLOR]'

        channel_name = ch['name']
        channel_thumb = ch['thumbnail']

        opciones_channels.append(platformtools.listitem_to_select('[COLOR yellow]' + channel_name + '[/COLOR]', info, channel_thumb))

        canales_no_actives.append((ch['name'], info, ch['notes']))

    ret = platformtools.dialog_select(cabecera, opciones_channels, useDetails=True)

    if not ret == -1:
        canal = canales_no_actives[ret]
        tests_channels(canal[0], canal[1], canal[2])


def only_prefered(item):
    logger.info()

    cabecera = 'Canales Preferidos'
    filtros = {'searchable': True}

    opciones_channels = []
    canales_only_prefered = []

    ch_list = channeltools.get_channels_list(filtros=filtros)

    i = 0
    for ch in ch_list:
        if not ch['status'] == 1:
            continue

        i =+1

    if i == 0:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin canales preferidos[/B][/COLOR]' % color_adver)
        return

    for ch in ch_list:
        if not ch['status'] == 1:
            continue

        cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'
        cfg_proxytools_max_channel = 'channel_' + ch['id'] + '_proxytools_max'
        cfg_proxytools_provider = 'channel_' + ch['id'] + '_proxytools_provider'

        info = ''

        info = info + '[B][COLOR %s][I] Preferido [/I][/B][/COLOR]' % color_list_prefe

        if 'dominios' in ch['notes'].lower():
            dominio = config.get_setting('channel_' + ch['id'] + '_dominio', default='')
            if dominio:
                dominio = dominio.replace('https://', '').replace('/', '')
                info = info + '[B][COLOR cyan] %s [/B][/COLOR]' % dominio

        if config.get_setting(cfg_proxies_channel, default=''):
            info = info + '[B][COLOR %s] Proxies [/B][/COLOR]' % color_list_proxies
        elif config.get_setting(cfg_proxytools_provider, default=''):
            info = info + '[COLOR yellowgreen][B] Sin proxies [/B][/COLOR]'
        elif config.get_setting(cfg_proxytools_max_channel, default=''):
            info = info + '[COLOR yellowgreen][B] Sin proxies [/B][/COLOR]'

        tipos = ch['search_types']
        tipos = str(tipos).replace('[', '').replace(']', '').replace("'", '')
        tipos = str(tipos).replace('movie', 'Películas').replace('tvshow', 'Series').replace('documentary', 'Documentales').replace('all,', '')

        if info: info = info + '  '
        info = info + '[COLOR mediumspringgreen][B]' + tipos + '[/B][/COLOR]'

        idiomas = ch['language']
        idiomas = str(idiomas).replace('[', '').replace(']', '').replace("'", '')
        idiomas = str(idiomas).replace('cast', 'Esp').replace('lat', 'Lat').replace('vose', 'Vose')

        if info: info = info + '  '
        info = info + '[COLOR mediumaquamarine]' + idiomas + '[/COLOR]'

        channel_name = ch['name']
        channel_thumb = ch['thumbnail']

        opciones_channels.append(platformtools.listitem_to_select('[COLOR yellow]' + channel_name + '[/COLOR]', info, channel_thumb))

        canales_only_prefered.append((ch['name'], info, ch['notes']))

    ret = platformtools.dialog_select(cabecera, opciones_channels, useDetails=True)

    if not ret == -1:
        canal = canales_only_prefered[ret]
        tests_channels(canal[0], canal[1], canal[2])


def only_torrents(item):
    logger.info()

    cabecera = 'Canales que pueden contener archivos Torrents'
    filtros = {'categories': 'torrent' ,'searchable': True}

    opciones_channels = []
    canales_torrents = []

    ch_list = channeltools.get_channels_list(filtros=filtros)

    if not ch_list:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin canales de este tipo[/B][/COLOR]' % color_adver)
        return

    for ch in ch_list:
        info = ''

        if ch['status'] == 1:
            info = info + '[B][COLOR %s][I] Preferido [/I][/B][/COLOR]' % color_list_prefe
        elif ch['status'] == -1:
            info = info + '[B][COLOR %s][I] Desactivado [/I][/B][/COLOR]' % color_list_inactive

        if 'dominios' in ch['notes'].lower():
            dominio = config.get_setting('channel_' + ch['id'] + '_dominio', default='')
            if dominio:
                dominio = dominio.replace('https://', '').replace('/', '')
                info = info + '[B][COLOR cyan] %s [/B][/COLOR]' % dominio

        cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'
        if config.get_setting(cfg_proxies_channel, default=''):
            info = info + '[B][COLOR %s] Proxies [/B][/COLOR]' % color_list_proxies

        tipos = ch['search_types']
        tipos = str(tipos).replace('[', '').replace(']', '').replace("'", '')
        tipos = str(tipos).replace('movie', 'Películas').replace('tvshow', 'Series').replace('documentary', 'Documentales').replace('all,', '')

        if info: info = info + '  '
        info = info + '[COLOR mediumspringgreen][B]' + tipos + '[/B][/COLOR]'

        idiomas = ch['language']
        idiomas = str(idiomas).replace('[', '').replace(']', '').replace("'", '')
        idiomas = str(idiomas).replace('cast', 'Esp').replace('lat', 'Lat').replace('vose', 'Vose')

        if info: info = info + '  '
        info = info + '[COLOR mediumaquamarine]' + idiomas + '[/COLOR]'

        channel_name = ch['name']
        channel_thumb = ch['thumbnail']

        opciones_channels.append(platformtools.listitem_to_select('[COLOR yellow]' + channel_name + '[/COLOR]', info, channel_thumb))

        canales_torrents.append((ch['name'], info, ch['notes']))

    ret = platformtools.dialog_select(cabecera, opciones_channels, useDetails=True)

    if not ret == -1:
        canal = canales_torrents[ret]
        tests_channels(canal[0], canal[1], canal[2])


def channels_excluded(item):
    logger.info()

    if item.extra == 'movies':
        cabecera = 'Películas'
        filtros = {'categories': 'movie', 'searchable': True}
    elif item.extra == 'tvshows':
        cabecera = 'Series'
        filtros = {'categories': 'tvshow', 'searchable': True}
    elif item.extra == 'documentaries':
        cabecera = 'Documentales'
        filtros = {'categories': 'documentary' ,'searchable': True}
    elif item.extra == 'mixed':
        cabecera = 'Películas y/o Series'
        filtros = {'searchable': True}

    else:
        cabecera = 'Todos'
        filtros = {'searchable': True}

    preselect = []
    channels_ids = []
    opciones = []

    cfg_excludes = 'search_excludes_' + item.extra
    channels_search = config.get_setting(cfg_excludes, default='')

    ch_list = channeltools.get_channels_list(filtros=filtros)

    if channels_search:
        channels_orden = []

        i = 0
        for ch in ch_list:
            channels_orden.append(ch['id'])
            i += 1

        channels_preselct = str(channels_search).replace('[', '').replace(']', ',')

        matches = scrapertools.find_multiple_matches(channels_preselct, "(.*?), '(.*?)',")
        for ch_nro, ch_name in matches:
            if not ch_name in channels_orden[int(ch_nro)]:
                tex1 = '[COLOR plum]El orden de la lista de los canales ha variado respecto a su lista anterior (Preferidos, Desactivados, Inactivos ó Anulados).[/COLOR]'
                tex2 = '[COLOR cyan][B]Deberá seleccionar de nuevo los canales a excluir deseados.[/B][/COLOR]'
                tex3 = '[COLOR red]Porque se eliminan los canales memorizados para excluirlos de [COLOR yellow] Configurar proxies a usar [/COLOR]'
                platformtools.dialog_ok(config.__addon_name, tex1, tex2, tex3)
                config.set_setting(cfg_excludes, '')
                preselect = []
                break

            ch_nro = ch_nro.strip()
            preselect.append(int(ch_nro))

    i = 0
    for ch in ch_list:
        if ch['searchable'] == False: continue

        if item.extra == 'mixed':
            tipos = ch['search_types']
            if 'documentary' in tipos: continue

        if not channels_search: preselect.append(i)
        channels_ids.append(ch['id'])
        i += 1

    for ch in ch_list:
        if ch['searchable'] == False: continue

        if item.extra == 'mixed':
            tipos = ch['search_types']
            if 'documentary' in tipos: continue

        info = ''

        if channels_search:
            channels_preselct = str(channels_search).replace('[', '').replace(']', ',')
            if ("'" + ch['id'] + "'") in str(channels_preselct):
                info = info + '[COLOR white][B]EXCLUIDO [/B][/COLOR]'

        if ch['status'] == 1:
            info = info + '[B][COLOR %s][I] Preferido [/I][/B][/COLOR]' % color_list_prefe
        elif ch['status'] == -1:
            info = info + '[B][COLOR %s][I] Desactivado [/I][/B][/COLOR]' % color_list_inactive

        if 'dominios' in ch['notes'].lower():
            dominio = config.get_setting('channel_' + ch['id'] + '_dominio', default='')
            if dominio:
                dominio = dominio.replace('https://', '').replace('/', '')
                info = info + '[B][COLOR cyan] %s [/B][/COLOR]' % dominio

        cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'
        if config.get_setting(cfg_proxies_channel, default=''):
            info = info + '[B][COLOR %s] Proxies [/B][/COLOR]' % color_list_proxies

        tipos = ch['search_types']
        tipos = str(tipos).replace('[', '').replace(']', '').replace("'", '')
        tipos = str(tipos).replace('movie', 'Películas').replace('tvshow', 'Series').replace('documentary', 'Documentales').replace('all,', '')

        if info: info = info + '  '
        info = info + '[COLOR mediumspringgreen][B]' + tipos + '[/B][/COLOR]'

        idiomas = ch['language']
        idiomas = str(idiomas).replace('[', '').replace(']', '').replace("'", '')
        idiomas = str(idiomas).replace('cast', 'Esp').replace('lat', 'Lat').replace('vose', 'Vose')

        if info: info = info + '  '
        info = info + '[COLOR mediumaquamarine]' + idiomas + '[/COLOR]'

        it = xbmcgui.ListItem(ch['name'], info)
        it.setArt({'thumb': ch['thumbnail']})
        opciones.append(it)

    ret = xbmcgui.Dialog().multiselect('Excluir canales en las búsquedas de  [COLOR yellow]' + cabecera + '[/COLOR]', opciones, preselect=preselect, useDetails=True)

    if ret is None: return

    seleccionados = channels_excluded_list(ret, channels_ids, channels_search)

    if str(seleccionados) == '[]': seleccionados = ''
    config.set_setting(cfg_excludes, str(seleccionados))

    platformtools.itemlist_refresh()


def channels_excluded_del(item):
    logger.info()

    if item.extra == 'movies':
        canales_excluidos = channels_search_excluded_movies
        txt = 'Películas'
    elif item.extra == 'tvshows':
        canales_excluidos = channels_search_excluded_tvshows
        txt = 'Series'
    elif item.extra == 'documentaries':
        canales_excluidos = channels_search_excluded_documentaries
        txt = 'Documentales'
    elif item.extra == 'mixed':
        canales_excluidos = channels_search_excluded_mixed
        txt = 'Películas y/o Series'
    else:
        canales_excluidos = channels_search_excluded_all
        txt = 'Películas, Series y Documentales'

    canales_excluidos = scrapertools.find_multiple_matches(str(canales_excluidos), "(.*?), '(.*?)'")

    txt_excluidos = ''

    for orden_nro, id_canal in canales_excluidos:
        if not txt_excluidos: txt_excluidos = id_canal.capitalize()
        else: txt_excluidos += (', ' + id_canal.capitalize())

    if not platformtools.dialog_yesno(config.__addon_name, '[COLOR plum]' + str(txt_excluidos) + '[/COLOR]', '[COLOR red]¿ Desea anular los canales memorizados para excluirlos en las búsquedas de ? [COLOR yellow] ' + txt + '[/COLOR]'):
        return

    if item.extra == 'movies':
        config.set_setting(cfg_search_excluded_movies, '')
    elif item.extra == 'tvshows':
        config.set_setting(cfg_search_excluded_tvshows, '')
    elif item.extra == 'documentaries':
        config.set_setting(cfg_search_excluded_documentaries, '')
    elif item.extra == 'mixed':
        config.set_setting(cfg_search_excluded_mixed, '')
    else:
        if channels_search_excluded_movies: config.set_setting(cfg_search_excluded_movies, '')
        if channels_search_excluded_tvshows: config.set_setting(cfg_search_excluded_tvshows, '')
        if channels_search_excluded_documentaries: config.set_setting(cfg_search_excluded_documentaries, '')
        if channels_search_excluded_mixed: config.set_setting(cfg_search_excluded_mixed, '')
        if channels_search_excluded_all: config.set_setting(cfg_search_excluded_all, '')

    platformtools.itemlist_refresh()


def channels_excluded_list(ret, channels_ids, channels_search):
    logger.info()

    channel_sel = []
    seleccionados = []

    if channels_search:
        for ch in ret:
            channel_sel.append(ch)
    else:
        nro_sel = 0
        for ch in ret:
            if not ch == nro_sel:
                channel_sel.append(nro_sel)
                nro_sel += 1

                while not (nro_sel == ch):
                    channel_sel.append(nro_sel)
                    nro_sel += 1

            nro_sel += 1

    for ch_sel in channel_sel:
        seleccionados.append(ch_sel)
        i_id = 0

        for channel_id in channels_ids:
            if ch_sel == i_id: seleccionados.append(channel_id)
            i_id += 1

    return seleccionados


def show_servers_list(item):
    import os

    from core import filetools, jsontools

    logger.info()

    if item.tipo == 'activos':
        cabecera = 'Servidores Disponibles'
        filtro = True
    elif item.tipo == 'inactivos':
        cabecera = 'Servidores Inactivos'
        filtro = False
    elif item.tipo == 'sinsoporte':
        cabecera = 'Servidores No Soportados'
        filtro = False
    else:
        cabecera = 'Todos los Servidores'
        filtro = None

    channels_ids = []
    opciones_servers = []
    servers = []

    path = os.path.join(config.get_runtime_path(), 'servers')

    servidores = os.listdir(path)

    if not servidores:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin servidores de este tipo[/B][/COLOR]' % color_adver)
        return

    thumb = config.get_thumb('bolt')

    for server in servidores:
        if not server.endswith('.json'): continue

        path_server = os.path.join(config.get_runtime_path(), 'servers', server)

        if not os.path.isfile(path_server): continue

        data = filetools.read(path_server)
        dict_server = jsontools.load(data)

        if not filtro is None:
            if filtro == False:
                if dict_server['active'] == True: continue
            else:
                if dict_server['active'] == False: continue

        info = ''

        try:
           notes = dict_server['notes']
        except: 
           notes = ''

        if item.tipo == 'sinsoporte':
            if not "Requiere" in notes: continue
			
        if dict_server['active'] == False:
            info = info + '[COLOR red][B] Inactivo [/B][/COLOR]'

        if notes:
            if info: info = info + '  '
            info = info + '[COLOR mediumaquamarine]' + notes + '[/COLOR]'

        server_name = dict_server['name']
        server_thumb = thumb

        opciones_servers.append(platformtools.listitem_to_select('[COLOR yellow]' + server_name + '[/COLOR]', info, server_thumb))

        servers.append((server_name, info))

    ret = platformtools.dialog_select(cabecera, opciones_servers, useDetails=True)

    if not ret == -1:
        servidor = servers[ret]
        tests_servers(servidor[0], servidor[1])


def show_channels_list(item):
    logger.info()

    channels_search_movies = config.get_setting(cfg_search_excluded_movies, default='')
    channels_search_tvshows = config.get_setting(cfg_search_excluded_tvshows, default='')
    channels_search_documentaries = config.get_setting(cfg_search_excluded_documentaries, default='')
    channels_search_mixed = config.get_setting(cfg_search_excluded_mixed, default='')
    channels_search_all = config.get_setting(cfg_search_excluded_all, default='')

    channels_search = channels_search_movies + channels_search_tvshows + channels_search_documentaries + channels_search_mixed + channels_search_all

    no_proxies = config.get_setting('search_no_proxies', default=False)
    no_channels = config.get_setting('search_no_channels', default=False)

    opciones_channels = []
    canales = []

    if item.no_active == True:
        filtros = {'active': False}
    elif item.no_stable == True:
        filtros = {'clusters': 'inestable'}
    else:
        filtros = {}

    ch_list = channeltools.get_channels_list(filtros=filtros)

    if not ch_list:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin canales de este tipo[/B][/COLOR]' % color_adver)
        return

    for ch in ch_list:
        info = ''

        cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'

        if ch['active'] == False:
            info = info + '[COLOR red][B] Inactivo [/B][/COLOR]'
        elif ch['searchable'] == False:
            info = info + '[COLOR coral][B] No búsquedas [/B][/COLOR]'
        elif channels_search:
            if no_proxies:
                if 'proxies' in ch['notes'].lower():
                    if config.get_setting(cfg_proxies_channel, default=''):
                        if no_channels:
                            info = info + '[COLOR moccasin][B] Descartado Proxies [/B][/COLOR]'

            if ch['id'] in channels_search:
                info = info + '[COLOR coral][B] No búsquedas [/B][/COLOR]'

        if ch['status'] == 1:
            info = info + '[B][COLOR %s][I] Preferido [/I][/B][/COLOR]' % color_list_prefe
        elif ch['status'] == -1:
            info = info + '[B][COLOR %s][I] Desactivado [/I][/B][/COLOR]' % color_list_inactive

        if 'dominios' in ch['notes'].lower():
            dominio = config.get_setting('channel_' + ch['id'] + '_dominio', default='')
            if dominio:
                dominio = dominio.replace('https://', '').replace('/', '')
                info = info + '[B][COLOR cyan] %s [/B][/COLOR]' % dominio

        if config.get_setting(cfg_proxies_channel, default=''):
            info = info + '[B][COLOR %s] Proxies [/B][/COLOR]' % color_list_proxies

        tipos = ch['search_types']
        tipos = str(tipos).replace('[', '').replace(']', '').replace("'", '')
        tipos = str(tipos).replace('movie', 'Películas').replace('tvshow', 'Series').replace('documentary', 'Documentales').replace('all,', '')

        if info: info = info + '  '
        info = info + '[COLOR mediumspringgreen][B]' + tipos + '[/B][/COLOR]'

        idiomas = ch['language']
        idiomas = str(idiomas).replace('[', '').replace(']', '').replace("'", '')
        idiomas = str(idiomas).replace('cast', 'Esp').replace('lat', 'Lat').replace('vose', 'Vose')

        if info: info = info + '  '
        info = info + '[COLOR mediumaquamarine]' + idiomas + '[/COLOR]'

        channel_name = ch['name']
        channel_thumb = ch['thumbnail']

        opciones_channels.append(platformtools.listitem_to_select('[COLOR yellow]' + channel_name + '[/COLOR]', info, channel_thumb))

        canales.append((ch['name'], info, ch['notes']))

    if item.no_active == True:
        cabecera = 'Canales [COLOR yellow]Inactivos[/COLOR]'
    elif item.no_stable == True:
        cabecera = 'Canales [COLOR yellow]Inestables[/COLOR]'
    else:
        cabecera = 'Canales [COLOR yellow]Disponibles[/COLOR]'

    ret = platformtools.dialog_select(cabecera, opciones_channels, useDetails=True)

    if not ret == -1:
        canal = canales[ret]
        tests_channels(canal[0], canal[1], canal[2])

def show_clients_torrent(item):
    logger.info()

    import os, xbmc

    from core import jsontools
    torrent_clients = jsontools.get_node_from_file('torrent.json', 'clients', os.path.join(config.get_runtime_path(), 'servers'))

    opciones_torrent = []
    torrents = []

    thumb = config.get_thumb('cloud')

    for client in torrent_clients:
        client_name = str(client['name']).capitalize()
        client_id = str(client['id'])

        if xbmc.getCondVisibility('System.HasAddon("%s")' % client['id']):
           exists_torrent = ' [COLOR yellow][B] Instalado [/B]'
        else:
           exists_torrent = ' [COLOR red][B] No instalado [/B]'

        opciones_torrent.append(platformtools.listitem_to_select('[COLOR cyan]' + client_name + '[/COLOR]', '[COLOR moccasin]' + client_id + exists_torrent + '[/COLOR]', thumb))

        torrents.append((client_name, client_id + exists_torrent))

    ret = platformtools.dialog_select('Clientes externos para [COLOR yellow]Torrents[/COLOR]', opciones_torrent, useDetails=True)

    if not ret == -1:
        if 'soportados' in item.title:
            torrent = torrents[ret]
            platformtools.dialog_ok(torrent[0], torrent[1] + '[/COLOR]')

    return ret


def tests_channels(canal_0, canal_1, canal_2):
    if platformtools.dialog_yesno(canal_0, canal_1, canal_2, '[COLOR coral]¿ Efectuar Test Status del Canal ?[/COLOR]'):
        from modules import tester
        tester.test_channel(canal_0)


def tests_servers(servidor_0, servidor_1):
    if platformtools.dialog_yesno(servidor_0, servidor_1, '[COLOR plum]¿ Efectuar Test Status del Servidor ?[/COLOR]'):
        from modules import tester
        tester.test_server(servidor_0)
