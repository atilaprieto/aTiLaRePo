# -*- coding: utf-8 -*-

import os, time
from threading import Thread

from platformcode import config, logger, platformtools
from core.item import Item
from core import channeltools


def mainlist(item):
    logger.info()
    itemlist = []

    thumb_filmaffinity = os.path.join(config.get_runtime_path(), 'resources', 'media', 'channels', 'thumb', 'filmaffinity.jpg')
    thumb_tmdb = os.path.join(config.get_runtime_path(), 'resources', 'media', 'channels', 'thumb', 'tmdb.jpg')

    item.category = 'Buscar'

    itemlist.append(item.clone( channel='tmdblists', action='mainlist', title='Búsquedas y listas en TMDB', thumbnail=thumb_tmdb,
                                plot = 'Buscar personas y ver listas de películas y series de la base de datos de The Movie Database' ))

    itemlist.append(item.clone( channel='filmaffinitylists', action='mainlist', title='Listas en Filmaffinity', thumbnail=thumb_filmaffinity,
                                plot = 'Ver listas de películas, series, documentales y otros de Filmaffinity' ))

    if config.get_setting('channels_link_main', default=True):
        itemlist.append(item.clone( action='search', search_type='all', title='Buscar Película y/o Serie ...',
                                    plot = 'Buscar indistintamente películas y/o series en todos los canales' ))

    itemlist.append(item.clone( action='search', search_type='movie', title='Buscar Película ...', thumbnail=config.get_thumb('movie'),
                                plot = 'Escribir el nombre de una película para buscarla en los canales de películas' ))

    itemlist.append(item.clone( action='search', search_type='tvshow', title='Buscar Serie ...', thumbnail=config.get_thumb('tvshow'),
                                plot = 'Escribir el nombre de una serie para buscarla en los canales de series' ))

    itemlist.append(item.clone( action='search', search_type='documentary', title='Buscar Documental ...', thumbnail=config.get_thumb('documentary'),
                                plot = 'Escribir el nombre de un documental para buscarlo en los canales de documentales' ))

    itemlist.append(item.clone( channel='actions', title= 'Configuración', action = 'open_settings', folder=False, thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( channel='filters', title = 'Excluir canales en las búsquedas', action = 'mainlist', text_color='cyan' ))

    itemlist.append(item.clone( action='show_help', title='Información búsquedas', folder=False, thumbnail=config.get_thumb('help'), text_color='green' ))

    return itemlist


def show_help(item):
    txt = 'Desde la configuración del addon se puede definir el número de resultados que se previsualizan para cada canal.'
    txt += ' Si por ejemplo el canal devuelve 15 resultados y se previsualizan 2, entrar en el enlace de la búsqueda para verlos todos.'
    txt += '[CR]'
    txt += '[CR]Según cada web/canal su buscador puede permitir diferenciar por películas/series o no, y también es variable la sensibilidad de la búsqueda (si busca sólo en el título o también en la sinopsis, el tratamiento si hay varias palabras, si devuelve muchos o pocos resultados, etc)'
    txt += '[CR]'
    txt += '[CR]Desde cualquier película/serie mostrada en el addon, acceder al menú contextual para buscar esa misma película/serie en los demás canales.'
    txt += '[CR]'
    txt += '[CR]Desde cualquier película/serie guardada en enlaces, si al acceder se produce un error en la web, se ofrece un diálogo para volver a buscar esa misma película/serie en los demás canales o en el mismo canal (por si han cambiado las urls de la web y el enlace ya no funciona).'

    platformtools.dialog_textviewer('Información sobre búsquedas', txt)
    return True


def search(item, tecleado):
    logger.info()

    item.category = 'Buscar ' + tecleado
    if item.search_type == '': item.search_type = 'all'

    itemlist = do_search(item, tecleado)

    return itemlist


def do_search_channel(item, tecleado, ch):
    canal = __import__('channels.' + item.channel, fromlist=[''])
    if hasattr(canal, 'search'):
        ch['itemlist_search'] = canal.search(item, tecleado)
    else:
        logger.error('Search not found in channel %s. Implementar search o quitar searchable!' % item.channel)


def do_search(item, tecleado):
    itemlist = []
    # De item se usa .search_type y .from_channel

    multithread = config.get_setting('search_multithread', default=True)
    threads = []
    search_limit_by_channel = config.get_setting('search_limit_by_channel', default=2)

    progreso = platformtools.dialog_progress('Buscando '+tecleado, '...')

    # Seleccionar los canales dónde se puede buscar
    filtros = { 'searchable': True, 'status': 0 } # status para descartar desactivados por el usuario, solamente se busca en activos y preferidos
    if item.search_type != 'all': filtros['search_types'] = item.search_type

    ch_list = channeltools.get_channels_list(filtros=filtros)
    if item.from_channel != '': # descartar from_channel (búsqueda en otros canales)
        ch_list = [ch for ch in ch_list if ch['id'] != item.from_channel]
    if item.search_type == 'all': # descartar documentary cuando 'all'
        ch_list = [ch for ch in ch_list if 'documentary' not in ch['categories']]

    num_canales = float(len(ch_list)) # float para calcular porcentaje

    no_proxies = config.get_setting('search_no_proxies', default=False)
    only_prefered = config.get_setting('search_only_prefered', default=False)
    no_channels = config.get_setting('search_no_channels', default=False)

    if item.search_type == 'movie':
        channels_search_excluded = config.get_setting('search_excludes_movies', default='')

    elif item.search_type == 'tvshow':
        channels_search_excluded = config.get_setting('search_excludes_tvshows', default='')

    elif item.search_type == 'documentary':
        channels_search_excluded = config.get_setting('search_excludes_documentaries', default='')

    else:
        channels_search_excluded = config.get_setting('search_excludes_mixed', default='')
        channels_search_excluded = channels_search_excluded + config.get_setting('search_excludes_all', default='')

    # Hacer la búsqueda en cada canal
    for i, ch in enumerate(ch_list):
        perc = int(i / num_canales * 100)

        progreso.update(perc, 'Analizar %s  en el canal %s ' % (tecleado, ch['name']))

        c_item = Item( channel=ch['id'], action='search', search_type=item.search_type, title='Buscar en '+ch['name'], thumbnail=ch['thumbnail'] )

        if no_proxies:
            cfg_proxies_channel = 'channel_' + ch['name'].lower() + '_proxies'
            if config.get_setting(cfg_proxies_channel, default=''):
                if no_channels:
                    platformtools.dialog_notification(ch['name'], '[COLOR red]Ignorado por proxies[/COLOR]')
                continue

        if channels_search_excluded:
            channels_preselct = str(channels_search_excluded).replace('[', '').replace(']', ',')
            if ("'" + ch['id'] + "'") in str(channels_preselct):
                if no_channels:
                    platformtools.dialog_notification(ch['name'], '[COLOR cyan]Ignorado por excluido[/COLOR]')
                continue

        if item.only_channels_group:
            if not ("'" + ch['id'] + "'") in str(item.only_channels_group): continue
        else:
            if only_prefered:
                cfg_status_channel = 'channel_' + ch['name'].lower() + '_status'
                if not config.get_setting(cfg_status_channel, default=''):
                    continue

        if multithread:
            t = Thread(target=do_search_channel, args=[c_item, tecleado, ch], name=ch['name'])
            t.setDaemon(True)
            t.start()
            threads.append(t)
        else:
            do_search_channel(c_item, tecleado, ch)

        if progreso.iscanceled(): break

    if multithread: # bucle de espera hasta que acabe o se cancele
        pendent = [a for a in threads if a.isAlive()]
        while len(pendent) > 0:
            hechos = num_canales - len(pendent)
            perc = int(hechos / num_canales * 100)
            mensaje = ', '.join([a.getName() for a in pendent])

            progreso.update(perc, 'Buscando %d de %d canales. Quedan %d : %s' % (hechos, num_canales, len(pendent), mensaje))

            if progreso.iscanceled(): break

            time.sleep(0.5)
            pendent = [a for a in threads if a.isAlive()]


    # Mostrar resultados de las búsquedas
    if item.from_channel != '': 
        # Búsqueda exacta en otros/todos canales de una peli/serie : mostrar sólo las coincidencias exactas
        tecleado_lower = tecleado.lower()
        for ch in ch_list:
            if 'itemlist_search' in ch and len(ch['itemlist_search']) > 0:
                for it in ch['itemlist_search']:
                    if it.contentType not in ['movie','tvshow','season']: continue # paginaciones
                    if it.infoLabels['tmdb_id'] and item.infoLabels['tmdb_id']:
                        if it.infoLabels['tmdb_id'] != item.infoLabels['tmdb_id']: continue
                    else:
                        if it.contentType == 'movie' and it.contentTitle.lower() != tecleado_lower: continue
                        if it.contentType in ['tvshow','season'] and it.contentSerieName.lower() != tecleado_lower: continue
                    it.title += ' [COLOR gold][%s][/COLOR]' % ch['name']
                    itemlist.append(it)

    else:
        # Búsqueda parecida en todos los canales : link para acceder a todas las coincidencias y previsualización de n enlaces por canal
        # Mover al final los canales que no tienen resultados
        # ~ for ch in ch_list:

        no_results = config.get_setting('search_no_results', default=False)

        color = 'chartreuse'
        titulo = ''

        for ch in sorted(ch_list, key=lambda ch: True if 'itemlist_search' not in ch or len(ch['itemlist_search']) == 0 else False):
            action = ''

            cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'

            if 'itemlist_search' in ch:
                if len(ch['itemlist_search']) == 0:
                    if no_results:
                        titulo = ch['name'] + '[COLOR moccasin] sin resultados'

                        if config.get_setting(cfg_proxies_channel, default=''):
                            titulo = titulo + ' [COLOR red]debe configurar nuevos proxies'
                    else:
                        if no_channels:
                            platformtools.dialog_notification(ch['name'], '[COLOR moccasin]Ignorado sin resultados[/COLOR]')
                        continue
                else:
                    action = 'search'
                    texto = 'resultados'
                    if len(ch['itemlist_search']) == 1: texto = 'resultado'
                    titulo = '%s [COLOR mediumspringgreen]... %d %s' % (ch['name'], len(ch['itemlist_search']), texto)
            else:
                if progreso.iscanceled():
                    titulo = '%s [COLOR mediumaquamarine]búsqueda cancelada' % ch['name']
                else:
                    if item.only_channels_group:
                        if not ("'" + ch['id'] + "'") in str(item.only_channels_group): continue

                    titulo = '%s [COLOR plum]No se ha buscado' % ch['name']

                    if no_proxies:
                        if config.get_setting(cfg_proxies_channel, default=''):
                            if no_channels:
                                titulo = '%s [COLOR red]Ignorado por proxies' % ch['name']
                        continue
                    else:
                       if only_prefered: continue

                       titulo = titulo + ' [COLOR red]comprobar si necesita proxies'

            if not titulo:
                itemlist.append(Item( action = '', title=tecleado +'[COLOR coral] sin resultados en ningún canal[/COLOR]' ))
                break

            titulo = '[B][COLOR %s]%s[/COLOR][/B]' % (color, titulo)
            itemlist.append(Item( channel=ch['id'], action=action, buscando=tecleado, title=titulo, thumbnail=ch['thumbnail'], search_type=item.search_type ))

            if 'itemlist_search' in ch:
                for j, it in enumerate(ch['itemlist_search']):
                    if it.contentType not in ['movie', 'tvshow', 'season']: continue # paginaciones
                    if j < search_limit_by_channel:
                        itemlist.append(it)
                    else:
                        break

            if 'búsqueda cancelada' in titulo: break

    progreso.close()

    if only_prefered:
        if len(itemlist) == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red]Búsqueda solo en preferidos[/COLOR]')

    return itemlist
