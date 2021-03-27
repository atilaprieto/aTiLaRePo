# -*- coding: utf-8 -*-

import os

from platformcode import config, logger, platformtools
from core.item import Item

from core import channeltools


# MAIN

def mainlist(item):
    logger.info()
    item.category = config.__addon_name

    itemlist = []

    if config.get_setting('developer_mode', default=False):
        if os.path.exists(os.path.join(config.get_runtime_path(), 'modules', 'developer.py')):
            itemlist.append(Item( channel='developer', action='mainlist', title='Gestión opción géneros', thumbnail=config.get_thumb('genres'), text_color='yellow' ))
        if os.path.exists(os.path.join(config.get_runtime_path(), 'modules', 'test.py')):
            itemlist.append(Item( channel='test', action='mainlist', title='Tests canales y servidores', thumbnail=config.get_thumb('tools'), text_color='moccasin' ))

    itemlist.append(Item( channel='search', action='mainlist', title='Buscar', thumbnail=config.get_thumb('search') ))

    if config.get_setting('channels_link_main', default=True):
        itemlist.append(item.clone( action='channels', extra='all', title='Canales', thumbnail=config.get_thumb('stack') ))

    itemlist.append(Item( channel='groups', action='mainlist', extra='groups', title='Grupos', thumbnail=config.get_thumb('bookshelf') ))

    itemlist.append(item.clone( action='channels', extra='movies', title='Películas', thumbnail=config.get_thumb('movie') ))

    itemlist.append(item.clone( action='channels', extra='tvshows', title='Series', thumbnail=config.get_thumb('tvshow') ))

    if config.get_setting('channels_link_pyse', default=False):
       itemlist.append(item.clone( action='channels', extra='mixed', title='Películas y Series', thumbnail=config.get_thumb('booklet') ))

    itemlist.append(Item( channel='generos', action='mainlist', title='Géneros', thumbnail=config.get_thumb('genres') ))

    itemlist.append(item.clone( action='channels', extra='documentaries', title='Documentales', thumbnail=config.get_thumb('documentary') ))

    if not config.get_setting('descartar_anime', default=True):
        itemlist.append(item.clone( action='channels', extra='anime', title='Animes', thumbnail=config.get_thumb('anime') ))

    if not config.get_setting('descartar_xxx', default=True):
        itemlist.append(item.clone( action='channels', extra='adults', title='Adultos', thumbnail=config.get_thumb('adults') ))

    itemlist.append(Item( channel='tracking', action='mainlist', title='Preferidos', thumbnail=config.get_thumb('videolibrary') ))

    itemlist.append(Item( channel='downloads', action='mainlist', title='Descargas', thumbnail=config.get_thumb('downloads') ))

    itemlist.append(Item( channel='helper', action='mainlist', title='Ayuda (%s)' % config.get_addon_version(), thumbnail=config.get_thumb('help') ))

    itemlist.append(Item( channel='actions', action='open_settings', title='Configuración', folder=False, thumbnail=config.get_thumb('settings') ))

    return itemlist


def channels(item):
    logger.info()
    itemlist = []

    thumb_filmaffinity = os.path.join(config.get_runtime_path(), 'resources', 'media', 'channels', 'thumb', 'filmaffinity.jpg')
    thumb_tmdb = os.path.join(config.get_runtime_path(), 'resources', 'media', 'channels', 'thumb', 'tmdb.jpg')

    if item.extra == 'movies':
        itemlist.append(Item( channel='search', action='search', search_type='movie', title='Buscar Película ...', thumbnail=config.get_thumb('search') ))

        if config.get_setting('search_extra_main', default=True):
            itemlist.append(Item( channel='tmdblists', action='mainlist', search_type='movie', title='Búsquedas y listas en TMDB', thumbnail=thumb_tmdb ))
            itemlist.append(Item( channel='filmaffinitylists', action='mainlist', search_type='movie', title='Listas en Filmaffinity',
                                  thumbnail=thumb_filmaffinity ))

        item.category = 'Canales con Películas'
        accion = 'mainlist_pelis'
        filtros = {'categories': 'movie', 'searchable': True}

    elif item.extra == 'tvshows':
        itemlist.append(Item( channel='search', action='search', search_type='tvshow', title='Buscar Serie ...', thumbnail=config.get_thumb('search') ))

        if config.get_setting('search_extra_main', default=True):
            itemlist.append(Item( channel='tmdblists', action='mainlist', search_type='tvshow', title='Búsquedas y listas en TMDB', thumbnail=thumb_tmdb ))
            itemlist.append(Item( channel='filmaffinitylists', action='mainlist', search_type='tvshow', title='Listas en Filmaffinity',
                                  thumbnail=thumb_filmaffinity ))

        item.category = 'Canales con Series'
        accion = 'mainlist_series'
        filtros = {'categories': 'tvshow', 'searchable': True}

    elif item.extra == 'documentaries':
        itemlist.append(Item( channel='search', action='search', search_type='documentary', title='Buscar Documental ...', thumbnail=config.get_thumb('search') ))

        if config.get_setting('search_extra_main', default=True):
            itemlist.append(Item( channel='filmaffinitylists', action='mainlist', search_type='documentary', title='Listas en Filmaffinity',
                                  thumbnail=thumb_filmaffinity ))

        item.category = 'Canales con Documentales'
        accion = 'mainlist'
        filtros = {'categories': 'documentary', 'searchable': True}

    elif item.extra == 'mixed':
        itemlist.append(Item( channel='search', action='search', search_type='all', extra = item.extra, title='Buscar Película y/o Serie ...',
                              thumbnail=config.get_thumb('search') ))

        if config.get_setting('search_extra_main', default=True):
            itemlist.append(Item( channel='tmdblists', action='mainlist', search_type='all', title='Búsquedas y listas en TMDB', thumbnail=thumb_tmdb ))
            itemlist.append(Item( channel='filmaffinitylists', action='mainlist', search_type='all', title='Listas en Filmaffinity',
                                  thumbnail=thumb_filmaffinity ))

        item.category = 'Canales con Películas y Series'
        accion = 'mainlist'
        filtros = {}

    else:
        if item.extra == 'adults': pass
        elif item.extra == 'anime': pass
        elif not item.extra == 'groups':
            itemlist.append(Item( channel='search', action='search', search_type='all', title='Buscar Película y/o Serie ...',
                                  thumbnail=config.get_thumb('search') ))

            if config.get_setting('search_extra_main', default=True):
                itemlist.append(Item( channel='tmdblists', action='mainlist', search_type='all', title='Búsquedas y listas en TMDB', thumbnail=thumb_tmdb ))
                itemlist.append(Item( channel='filmaffinitylists', action='mainlist', search_type='all', title='Listas en Filmaffinity',
                                      thumbnail=thumb_filmaffinity ))

            itemlist.append(Item( channel='search', action='search', search_type='documentary', title='Buscar Documental ...', thumbnail=config.get_thumb('search') ))

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
                itemlist.append(Item( channel='helper', action='show_help_adults', title='Informacion control parental', thumbnail=config.get_thumb('help'), text_color='green' ))

        accion = 'mainlist'
        filtros = {}

    channels_list_status = config.get_setting('channels_list_status', default=0) # 0:Todos, 1:preferidos+activos, 2:preferidos
    if channels_list_status > 0:
        filtros['status'] = 0 if channels_list_status == 1 else 1

    color_preferidos = config.get_setting('channels_list_prefe_color')

    ch_list = channeltools.get_channels_list(filtros=filtros)
    for ch in ch_list:
        if not item.extra == 'all':
            if ch['status'] == -1: continue

        context = []
        if ch['status'] != -1:
            context.append({'title': 'Marcar como Desactivado', 'channel': item.channel, 'action': 'marcar_canal', 'estado': -1})
        if ch['status'] != 0:
            context.append({'title': 'Marcar como Activo', 'channel': item.channel, 'action': 'marcar_canal', 'estado': 0})
        if ch['status'] != 1:
            context.append({'title': 'Marcar como Preferido', 'channel': item.channel, 'action': 'marcar_canal', 'estado': 1})

        color = color_preferidos if ch['status'] == 1 else 'white' if ch['status'] == 0 else 'gray'

        if item.extra == 'adults':
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

        plot = ''
        if item.extra == 'all': plot += '[' + ', '.join([config.get_localized_category(ct) for ct in ch['categories']]) + '][CR]'
        plot += '[' + ', '.join([idioma_canal(lg) for lg in ch['language']]) + ']'
        if ch['notes'] != '': plot += '[CR][CR]' + ch['notes']

        titulo = ch['name']
        if ch['status'] == -1: titulo += ' ([COLOR lightslategray][B][I]desactivado[/I][/B][/COLOR])'

        itemlist.append(Item( channel=ch['id'], action=accion, title=titulo, context=context, text_color=color, plot = plot,
                              thumbnail=ch['thumbnail'], category=ch['name'] ))

    return itemlist


def idioma_canal(lang):
    idiomas = { 'cast':'Castellano', 'lat':'Latino', 'eng':'Inglés', 'por':'Portugués', 'vo':'VO', 'vose':'VOSE', 'vos':'VOS', 'cat':'Català' }
    return idiomas[lang] if lang in idiomas else lang


def marcar_canal(item):
    logger.info()

    config.set_setting('status', item.estado, item.from_channel)

    platformtools.itemlist_refresh()
    return True


# ~ def marcar_servidor(item):
    # ~ logger.info()

    # ~ config.set_setting('status', item.estado, server=item.server)

    # ~ platformtools.itemlist_refresh()
    # ~ return True
