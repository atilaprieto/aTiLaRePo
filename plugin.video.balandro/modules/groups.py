# -*- coding: utf-8 -*-

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


def mainlist(item):
    logger.info()
    itemlist = []

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

    itemlist.append(Item( channel='search', action='mainlist', title='Buscar', context=context, thumbnail=config.get_thumb('search'), text_color='yellowgreen' ))

    item.category = 'Agrupaciones de Canales'

    itemlist.append(item.clone( title = 'Novedades:', action = '', text_color='yellow' ))
    itemlist.append(item.clone( title = ' Canales de Películas con Estrenos y/ó Novedades', action = 'ch_groups', group = 'news' ))
    itemlist.append(item.clone( title = ' Canales de Series con Episodios Nuevos y/ó Últimos', action = 'ch_groups', group = 'lasts' ))

    itemlist.append(item.clone( title = 'Películas y/ó Series:', action = '', text_color='springgreen' ))
    itemlist.append(item.clone( title = ' Canales con temática Clásica', action = 'ch_groups', group = 'classic' ))
    itemlist.append(item.clone( title = ' Canales con temática Infantil', action = 'ch_groups', group = 'kids' ))
    itemlist.append(item.clone( title = ' Canales que pueden contener enlaces Torrents', action = 'ch_groups', group = 'torrents' ))
    itemlist.append(item.clone( title = ' Canales con Rankings (Más vistas, Más valoradas, etc.)', action = 'ch_groups', group = 'rankings' ))
    itemlist.append(item.clone( title = ' Canales con Vídeos en Versión Original y/ó Subtitulada', action = 'ch_groups', group = 'vos' ))

    itemlist.append(item.clone( title = 'Películas:', action = '', text_color='cyan' ))
    itemlist.append(item.clone( title = ' Canales por Idiomas', action = 'ch_groups', group = 'languages' ))
    itemlist.append(item.clone( title = ' Canales por Años', action = 'ch_groups', group = 'years' ))
    itemlist.append(item.clone( title = ' Canales con Épocas', action = 'ch_groups', group = 'epochs' ))
    itemlist.append(item.clone( title = ' Canales por Países', action = 'ch_groups', group = 'countries' ))
    itemlist.append(item.clone( title = ' Canales por Calidades', action = 'ch_groups', group = 'qualityes' ))

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
        itemlist.append(item.clone( title = 'Anime:', action = '', thumbnail=config.get_thumb('anime'), text_color='pink' ))
        itemlist.append(item.clone( title = ' Canales con contenido Anime', action = 'ch_groups', group = 'anime', context=context ))

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    if not descartar_xxx:
        itemlist.append(item.clone( title = 'Adultos (+18):', action = '', thumbnail=config.get_thumb('adults'), text_color='red' ))
        itemlist.append(item.clone( title = ' Canales que pueden contener temática para Adultos', action = 'ch_groups', group = 'adults', context=context ))

    itemlist.append(item.clone( title = 'Documentales:', action = '', text_color='limegreen' ))
    itemlist.append(item.clone( title = ' Canales con temática de Documentales', action = 'ch_groups', group = 'docs' ))

    itemlist.append(item.clone( title = 'Especiales:', action = '', text_color='moccasin' ))
    itemlist.append(item.clone( title = ' Canales con Categorias', action = 'ch_groups', group = 'categories' ))
    itemlist.append(item.clone( title = ' Canales con Intérpretes', action = 'ch_groups', group = 'stars' ))
    itemlist.append(item.clone( title = ' Canales con Directores/as', action = 'ch_groups', group = 'directors' ))

    itemlist.append(item.clone( title = 'Diversos:', action = '', text_color='fuchsia' ))
    itemlist.append(item.clone( title = ' Canales con Productoras, Plataformas, y/ó Estudios', action = 'ch_groups', group = 'producers' ))
    itemlist.append(item.clone( title = ' Canales con Listas, Sagas, Colecciones, y/ó Otros', action = 'ch_groups', group = 'lists' ))
    itemlist.append(item.clone( title = ' Canales con Vídeos en 3D', action = 'ch_groups', group = '3d' ))

    return itemlist


def ch_groups(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)
    descartar_anime = config.get_setting('descartar_anime', default=False)

    accion = 'mainlist'

    search_type = ''
    if item.group == 'news': accion = 'mainlist_pelis'
    elif item.group == 'lasts': accion = 'mainlist_series'

    elif item.group == 'languages':
         accion = 'idiomas'
         search_type = 'movie'
    elif item.group == 'years':
         accion = 'anios'
         search_type = 'movie'
    elif item.group == 'epochs':
         search_type = 'movie'
    elif item.group == 'countries':
         accion = 'paises'
         search_type = 'movie'
    elif item.group == 'qualityes':
         accion = 'calidades'
         search_type = 'movie'

    elif item.group == 'categories': accion = 'categorias'

    canales = []
    filtros = {}

    ch_list = channeltools.get_channels_list(filtros=filtros)
    for ch in ch_list:
        try:
           agrupaciones = ch['clusters']
           if not item.group in agrupaciones: continue
        except:
           continue

        if ch['searchable'] == False: # para los porno
            if descartar_xxx:
                if 'adults' in agrupaciones:
                    if item.group == 'news': continue
                    elif item.group == 'rankings': continue
                    elif item.group == 'categories': continue
                    elif item.group == 'stars': continue

            elif descartar_anime:
                if 'anime' in agrupaciones:
                   if item.group == 'anime': continue

        action = accion
        if item.group == 'anime':
            if 'anime' in ch['notes'].lower():
                 action = 'mainlist_anime'
            else:
                 if ch['name'].startswith('Series'):
                     action = 'mainlist_series'
                 else:
                     if ch['name'] == 'Tekilaz':
                         action = 'mainlist_series'
                     else:
                         action = 'mainlist_pelis'

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
        plot += '[' + ', '.join([config.get_localized_category(ct) for ct in ch['categories']]) + '][CR]'
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
                              thumbnail=ch['thumbnail'], category=ch['name'], search_type = search_type, sort = 'C' ))

        if ch['status'] == -1: continue

        canales.append(ch['id'])

    if itemlist:
        buscar_only_group = True

        if item.group == 'categories': buscar_only_group = False
        elif item.group == 'stars': buscar_only_group = False
        elif item.group == 'directors': buscar_only_group = False
        elif item.group == 'producers': buscar_only_group = False
        elif item.group == 'lists': buscar_only_group = False
        elif item.group == 'adults': buscar_only_group = False

        if buscar_only_group:
            if len(itemlist) > 1:
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

                itemlist.append(Item( channel='search', action='search', search_type='all', title='Buscar solo en los canales de este grupo ...',
                                      context=context, only_channels_group = canales, group = item.group,
                                      thumbnail=config.get_thumb('search'), sort = 'B', text_color='yellowgreen' ))

    return sorted(itemlist, key=lambda it: it.sort)


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
