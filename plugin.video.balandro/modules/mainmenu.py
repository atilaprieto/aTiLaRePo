# -*- coding: utf-8 -*-

import os

from platformcode import config, logger
from core.item import Item

from core import channeltools

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
    item.category = config.__addon_name

    itemlist = []

    if config.get_setting('developer_mode', default=False):
        if os.path.exists(os.path.join(config.get_runtime_path(), 'modules', 'developer.py')):
            itemlist.append(Item( channel='developer', action='mainlist', title='Gestión opción géneros', thumbnail=config.get_thumb('genres'), text_color='yellow' ))
        if os.path.exists(os.path.join(config.get_runtime_path(), 'modules', 'test.py')):
            itemlist.append(Item( channel='test', action='mainlist', title='Tests canales y servidores', thumbnail=config.get_thumb('tools'), text_color='moccasin' ))
    
    itemlist.append(Item( channel='filmaffinitylists', action='oscars', title='[COLOR gold]Premios Oscars[/COLOR]', thumbnail=config.get_thumb('oscars'), plot = 'Especial con las películas nominadas a los premios [COLOR gold]Oscars[/COLOR]' ))

    context = []
    tit = '[COLOR %s]Global configurar proxies a usar[/COLOR]' % color_list_proxies
    context.append({'title': tit, 'channel': 'proxysearch', 'action': 'proxysearch_all'})

    if config.get_setting('proxysearch_excludes', default=''):
        tit = '[COLOR %s]Anular canales excluidos en Global ...[/COLOR]' % color_list_proxies
        context.append({'title': tit, 'channel': 'proxysearch', 'action': 'channels_proxysearch_del'})

    tit = '[COLOR %s]Información búsquedas[/COLOR]' % color_infor
    context.append({'title': tit, 'channel': 'search', 'action': 'show_help'})

    tit = '[COLOR %s]Ajustes categoría buscar[/COLOR]' % color_exec
    context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    itemlist.append(Item( channel='search', action='mainlist', title='Buscar', context=context, thumbnail=config.get_thumb('search') ))

    context = []
    tit = '[COLOR %s]Ajustes categoría canales[/COLOR]' % color_exec
    context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    if config.get_setting('channels_link_main', default=True):
        itemlist.append(item.clone( action='channels', extra='all', title='Canales', context=context, thumbnail=config.get_thumb('stack') ))

    itemlist.append(Item( channel='groups', action='mainlist', extra='groups', title='Grupos', thumbnail=config.get_thumb('bookshelf') ))

    itemlist.append(item.clone( action='channels', extra='movies', title='Películas', thumbnail=config.get_thumb('movie') ))

    itemlist.append(item.clone( action='channels', extra='tvshows', title='Series', thumbnail=config.get_thumb('tvshow') ))

    if config.get_setting('channels_link_pyse', default=False):
       itemlist.append(item.clone( action='channels', extra='mixed', title='Películas y Series', context=context, thumbnail=config.get_thumb('booklet') ))

    itemlist.append(Item( channel='generos', action='mainlist', title='Géneros', thumbnail=config.get_thumb('genres') ))

    itemlist.append(item.clone( action='channels', extra='documentaries', title='Documentales', thumbnail=config.get_thumb('documentary') ))

    context = []
    if config.get_setting('adults_password'):
        tit = '[COLOR %s]Eliminar Pin parental[/COLOR]' % color_infor
        context.append({'title': tit, 'channel': 'actions', 'action': 'adults_password_del'})

        tit = '[COLOR %s]Refrescar caché menú[/COLOR]' % color_adver
        context.append({'title': tit, 'channel': item.channel, 'action': '_refresh_menu'})
    else:
        tit = '[COLOR %s]Información parental[/COLOR]' % color_infor
        context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_adults'})

    tit = '[COLOR %s]Ajustes categoría canales[/COLOR]' % color_exec
    context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    if not config.get_setting('descartar_anime', default=True):
        itemlist.append(item.clone( action='channels', extra='anime', title='Animes', context=context, thumbnail=config.get_thumb('anime') ))

    if not config.get_setting('descartar_xxx', default=True):
        itemlist.append(item.clone( action='channels', extra='adults', title='Adultos', context=context, thumbnail=config.get_thumb('adults') ))

    context = []
    tit = '[COLOR %s]Información preferidos[/COLOR]' % color_infor
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_tracking'})

    tit = '[COLOR %s]Ajustes categoría preferidos[/COLOR]' % color_exec
    context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    itemlist.append(Item( channel='tracking', action='mainlist', title='Preferidos', context=context, thumbnail=config.get_thumb('videolibrary') ))

    context = []
    tit = '[COLOR %s]Ajustes categoría descargas[/COLOR]' % color_exec
    context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    itemlist.append(Item( channel='downloads', action='mainlist', title='Descargas', context=context, thumbnail=config.get_thumb('downloads') ))

    context = []
    tit = '[COLOR %s]Información versión[/COLOR]' % color_infor
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_version'})

    tit = '[COLOR %s]Comprobar actualizaciones Fix[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'actions', 'action': 'check_addon_updates'})

    tit = '[COLOR %s]Forzar actualizaciones Fix[/COLOR]' % color_adver
    context.append({'title': tit, 'channel': 'actions', 'action': 'check_addon_updates_force'})

    tit = '[COLOR %s]Test del sistema[/COLOR]' % color_alert
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_test'})

    tit = '[COLOR %s]Ajustes configuración[/COLOR]' % color_exec
    context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    itemlist.append(Item( channel='helper', action='mainlist', title='Ayuda (%s)' % config.get_addon_version(), context=context, thumbnail=config.get_thumb('help') ))

    itemlist.append(Item( channel='actions', action='open_settings', title='Configuración', folder=False, thumbnail=config.get_thumb('settings') ))

    return itemlist


def channels(item):
    logger.info()
    itemlist = []

    thumb_filmaffinity = os.path.join(config.get_runtime_path(), 'resources', 'media', 'channels', 'thumb', 'filmaffinity.jpg')
    thumb_tmdb = os.path.join(config.get_runtime_path(), 'resources', 'media', 'channels', 'thumb', 'tmdb.jpg')

    context = []
    tit = '[COLOR %s]Global configurar proxies a usar[/COLOR]' % color_list_proxies
    context.append({'title': tit, 'channel': 'proxysearch', 'action': 'proxysearch_all'})

    if config.get_setting('proxysearch_excludes', default=''):
        tit = '[COLOR %s]Anular canales excluidos en Global ...[/COLOR]' % color_list_proxies
        context.append({'title': tit, 'channel': 'proxysearch', 'action': 'channels_proxysearch_del'})

    tit = '[COLOR %s]Información búsquedas[/COLOR]' % color_infor
    context.append({'title': tit, 'channel': 'search', 'action': 'show_help'})

    tit = '[COLOR %s]Ajustes categoría buscar[/COLOR]' % color_exec
    context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    if item.extra == 'movies':
        itemlist.append(item.clone( channel='filters', action = 'channels_excluded', title = 'Excluir canales en las búsquedas de películas',
                                    extra = 'movies', thumbnail=config.get_thumb('stack'), folder = False, text_color='cyan' ))

        if channels_search_excluded_movies:
            itemlist.append(item.clone( channel='filters', action = 'channels_excluded_del', title = 'Anular los canales excluidos en las búsquedas de películas',
                                        extra = 'movies', folder = False, text_color='coral' ))

        itemlist.append(Item( channel='search', action='search', search_type='movie', title='Buscar Película ...', context=context,
                              thumbnail=config.get_thumb('search'), text_color='yellowgreen' ))

        if config.get_setting('search_extra_main', default=True):
            itemlist.append(Item( channel='tmdblists', action='mainlist', search_type='movie', title='Búsquedas y listas en TMDB',
                                  thumbnail=thumb_tmdb, text_color='yellowgreen' ))

            itemlist.append(Item( channel='filmaffinitylists', action='mainlist', search_type='movie', title='Listas en Filmaffinity',
                                  thumbnail=thumb_filmaffinity, text_color='yellowgreen' ))

        item.category = 'Canales con Películas'
        accion = 'mainlist_pelis'
        filtros = {'categories': 'movie'}

    elif item.extra == 'tvshows':
        itemlist.append(item.clone( channel='filters', action = 'channels_excluded', title = 'Excluir canales en las búsquedas de series',
                                    extra = 'tvshows', thumbnail=config.get_thumb('stack'), folder = False, text_color='cyan' ))

        if channels_search_excluded_tvshows:
            itemlist.append(item.clone( channel='filters', action = 'channels_excluded_del', title = 'Anular los canales excluidos en las búsquedas de series',
                                        extra = 'tvshows', folder = False, text_color='coral' ))

        itemlist.append(Item( channel='search', action='search', search_type='tvshow', title='Buscar Serie ...', context=context,
                              thumbnail=config.get_thumb('search'), text_color='yellowgreen' ))

        if config.get_setting('search_extra_main', default=True):
            itemlist.append(Item( channel='tmdblists', action='mainlist', search_type='tvshow', title='Búsquedas y listas en TMDB',
                                  thumbnail=thumb_tmdb, text_color='yellowgreen' ))

            itemlist.append(Item( channel='filmaffinitylists', action='mainlist', search_type='tvshow', title='Listas en Filmaffinity',
                                  thumbnail=thumb_filmaffinity, text_color='yellowgreen' ))

        item.category = 'Canales con Series'
        accion = 'mainlist_series'
        filtros = {'categories': 'tvshow'}

    elif item.extra == 'documentaries':
        itemlist.append(item.clone( channel='filters', action = 'channels_excluded', title = 'Excluir canales en las búsquedas de documentales',
                                    extra = 'documentaries', thumbnail=config.get_thumb('stack'), folder = False, text_color='cyan' ))

        if channels_search_excluded_documentaries:
            itemlist.append(item.clone( channel='filters', action = 'channels_excluded_del', title = 'Anular los canales excluidos en las búsquedas de documentales',
                                        extra = 'documentaries', folder = False, text_color='coral' ))

        itemlist.append(Item( channel='search', action='search', search_type='documentary', title='Buscar Documental ...', context=context,
                              thumbnail=config.get_thumb('search'), text_color='yellowgreen' ))

        if config.get_setting('search_extra_main', default=True):
            itemlist.append(Item( channel='filmaffinitylists', action='mainlist', search_type='documentary', title='Listas en Filmaffinity',
                                  thumbnail=thumb_filmaffinity, text_color='yellowgreen' ))

        item.category = 'Canales con Documentales'
        accion = 'mainlist'
        filtros = {'categories': 'documentary', 'searchable': True}

    elif item.extra == 'mixed':
        itemlist.append(item.clone( channel='filters', action = 'channels_excluded', title = 'Excluir canales en las búsquedas para Películas y/o Series',
                                    extra = 'mixed', thumbnail=config.get_thumb('stack'), folder = False, text_color='cyan' ))

        if channels_search_excluded_mixed:
            itemlist.append(item.clone( channel='filters', action = 'channels_excluded_del', title = 'Anular los canales excluidos en las búsquedas para Películas y/o Series',
                                        extra = 'mixed', folder = False, text_color='coral' ))

        itemlist.append(Item( channel='search', action='search', search_type='all', extra = item.extra, title='Buscar Película y/o Serie ...', context=context,
                              thumbnail=config.get_thumb('search'), text_color='yellowgreen' ))

        if config.get_setting('search_extra_main', default=True):
            itemlist.append(Item( channel='tmdblists', action='mainlist', search_type='all', title='Búsquedas y listas en TMDB',
	                              thumbnail=thumb_tmdb, text_color='yellowgreen' ))

            itemlist.append(Item( channel='filmaffinitylists', action='mainlist', search_type='all', title='Listas en Filmaffinity',
                                  thumbnail=thumb_filmaffinity, text_color='yellowgreen' ))

        item.category = 'Canales con Películas y Series'
        accion = 'mainlist'
        filtros = {}

    else:
        if item.extra == 'adults': pass
        elif item.extra == 'anime': pass
        elif not item.extra == 'groups':
            itemlist.append(item.clone( channel='filters', action = 'channels_excluded', title = 'Excluir canales en las búsquedas de Películas, Series y Documentales',
                                    extra = 'all', thumbnail=config.get_thumb('stack'), folder = False, text_color='cyan' ))

            if channels_search_excluded_all:
                itemlist.append(item.clone( channel='filters', action = 'channels_excluded_del', title = 'Anular los canales excluidos en las búsquedas de Películas, Series y Documentales',
                                        extra = 'all', folder = False, text_color='coral' ))

            itemlist.append(Item( channel='search', action='search', search_type='all', title='Buscar Película y/o Serie ...', context=context,
                                  thumbnail=config.get_thumb('search'), text_color='yellowgreen' ))

            if config.get_setting('search_extra_main', default=True):
                itemlist.append(Item( channel='tmdblists', action='mainlist', search_type='all', title='Búsquedas y listas en TMDB',
                                thumbnail=thumb_tmdb, text_color='yellowgreen' ))

                itemlist.append(Item( channel='filmaffinitylists', action='mainlist', search_type='all', title='Listas en Filmaffinity',
                                      thumbnail=thumb_filmaffinity, text_color='yellowgreen' ))

            itemlist.append(Item( channel='search', action='search', search_type='documentary', title='Buscar Documental ...', context=context,
	                              thumbnail=config.get_thumb('search'), text_color='yellowgreen' ))

        if item.extra == 'adults':
            item.category = 'Canales exclusivos para Adultos'
        elif item.extra == 'anime':
            item.category = 'Canales exclusivos de Animes'
        elif not item.extra == 'groups':
            item.category = 'Todos los Canales'
        else:
            item.category = 'Canales con Agrupaciones'

        if item.extra == 'adults' or item.extra == 'anime':
            if not config.get_setting('adults_password'):
                itemlist.append(Item( channel='helper', action='show_help_adults', title='Informacion parental', thumbnail=config.get_thumb('help'), text_color='green' ))

        accion = 'mainlist'
        filtros = {}

    channels_list_status = config.get_setting('channels_list_status', default=0) # 0:Todos, 1:preferidos+activos, 2:preferidos
    if channels_list_status > 0:
        filtros['status'] = 0 if channels_list_status == 1 else 1

    ch_list = channeltools.get_channels_list(filtros=filtros)
    for ch in ch_list:
        if item.extra == 'movies':
            if ch['searchable'] == False:
                if 'adults' in ch['clusters']: continue
                elif 'anime' in ch['clusters']: continue

        elif item.extra == 'tvshows':
            if ch['searchable'] == False:
                if 'adults' in ch['clusters']: continue
                elif 'anime' in ch['clusters']: continue

        elif item.extra == 'adults':
            if ch['searchable'] == True: continue
            if not 'adults' in ch['clusters']: continue

        elif item.extra == 'anime':
            if ch['searchable'] == True: continue
            if not 'anime' in ch['clusters']: continue

        elif item.extra == 'mixed':
            tipos = ch['search_types']
            if 'documentary' in tipos: continue

            if not 'movie' in tipos: continue
            if not 'tvshow' in tipos: continue

        context = []

        cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'

        if config.get_setting(cfg_proxies_channel, default=''):
            tit = '[COLOR %s]Quitar los proxies del canal[/COLOR]' % color_list_proxies
            context.append({'title': tit, 'channel': item.channel, 'action': '_quitar_proxies'})

        if ch['status'] != 1:
            tit = '[COLOR %s]Marcar canal como Preferido[/COLOR]' % color_list_prefe
            context.append({'title': tit, 'channel': item.channel, 'action': '_marcar_canal', 'estado': 1})
        if ch['status'] != 0:
            if ch['status'] == 1:
                tit = '[COLOR %s]Des-Marcar canal como Preferido[/COLOR]' % color_list_prefe
                context.append({'title': tit, 'channel': item.channel, 'action': '_marcar_canal', 'estado': 0})
            elif ch['status'] == -1:
                tit = '[COLOR %s]Des-Marcar canal como Desactivado[/COLOR]' % color_list_inactive
                context.append({'title': tit, 'channel': item.channel, 'action': '_marcar_canal', 'estado': 0})
            else:
                tit = '[COLOR white]Marcar canal como Activo[/COLOR]'
                context.append({'title': tit, 'channel': item.channel, 'action': '_marcar_canal', 'estado': 0})
        if ch['status'] != -1:
            tit = '[COLOR %s]Marcar canal como Desactivado[/COLOR]' % color_list_inactive
            context.append({'title': tit, 'channel': item.channel, 'action': '_marcar_canal', 'estado': -1})

        if 'dominios' in ch['notes'].lower():
            tit = '[COLOR %s]Configurar dominio a usar[/COLOR]' % color_adver
            context.append({'title': tit, 'channel': item.channel, 'action': '_dominios'})

        if 'proxies' in ch['notes'].lower():
            if not config.get_setting(cfg_proxies_channel, default=''):
                tit = '[COLOR %s]Información proxies[/COLOR]' % color_infor
                context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

            tit = '[COLOR %s]Cofigurar proxies a usar[/COLOR]' % color_list_proxies
            context.append({'title': tit, 'channel': item.channel, 'action': '_proxies'})

            tit = '[COLOR %s]Refrescar caché menú[/COLOR]' % color_exec
            context.append({'title': tit, 'channel': item.channel, 'action': '_refresh_menu'})

        color = color_list_prefe if ch['status'] == 1 else 'white' if ch['status'] == 0 else color_list_inactive

        plot = ''
        if item.extra == 'all': plot += '[' + ', '.join([config.get_localized_category(ct) for ct in ch['categories']]) + '][CR]'
        plot += '[' + ', '.join([idioma_canal(lg) for lg in ch['language']]) + ']'
        if ch['notes'] != '': plot += '[CR][CR]' + ch['notes']

        titulo = ch['name']

        if ch['status'] == -1:
            titulo += '[I][COLOR %s] (desactivado)[/COLOR][/I]' % color_list_inactive
            if config.get_setting(cfg_proxies_channel, default=''):
                titulo += '[I][COLOR %s] (proxies)[/COLOR][/I]' % color_list_proxies
        else:
            if config.get_setting(cfg_proxies_channel, default=''):
                if ch['status'] == 1:
                    titulo += '[I][COLOR %s] (proxies)[/COLOR][/I]' % color_list_proxies
                else:
                   color = color_list_proxies

        if 'inestable' in ch['clusters']:
            titulo += '[I][COLOR plum] (inestable)[/COLOR][/I]'
        elif 'register' in ch['clusters']:
            cfg_login_channel = 'channel_' + ch['id'] + '_' + ch['id'] +'_login'
            if not config.get_setting(cfg_login_channel, default=False):
               titulo += '[I][COLOR teal] (cuenta)[/COLOR][/I]'
            else:
               titulo += '[COLOR teal] (sesion)[/COLOR]'
			
        itemlist.append(Item( channel=ch['id'], action=accion, title=titulo, context=context, text_color=color, plot = plot,
                              thumbnail=ch['thumbnail'], category=ch['name'] ))

    return itemlist


def idioma_canal(lang):
    idiomas = { 'cast': 'Castellano', 'lat': 'Latino', 'eng': 'Inglés', 'pt': 'Portugués', 'vo': 'VO', 'vose': 'Vose', 'vos': 'Vos', 'cat': 'Català' }
    return idiomas[lang] if lang in idiomas else lang


def _marcar_canal(item):
    from modules import submnuctext
    submnuctext._marcar_canal(item)
    return True

def _refresh_menu(item):
    from modules import submnuctext
    submnuctext._refresh_menu(item)
    return True

def _quitar_proxies(item):
    from modules import submnuctext
    submnuctext._quitar_proxies(item)
    return True

def _dominios(item):
    from modules import submnuctext
    submnuctext._dominios(item)
    return True

def _proxies(item):
    from modules import submnuctext
    submnuctext._proxies(item)
    return True
