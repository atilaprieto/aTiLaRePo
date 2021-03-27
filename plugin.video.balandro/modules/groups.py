# -*- coding: utf-8 -*-

from platformcode import config, logger
from core.item import Item

from core import channeltools


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(Item( channel='search', action='mainlist', title='Buscar', thumbnail=config.get_thumb('search') ))

    item.category = 'Agrupaciones de Canales'

    itemlist.append(item.clone( title = 'Novedades:', action = '', text_color='yellow' ))
    itemlist.append(item.clone( title = ' - Canales de Películas con Estrenos y/ó Novedades', action = 'ch_groups', group = 'news' ))
    itemlist.append(item.clone( title = ' - Canales de Series con Episodios Nuevos y/ó Últimos', action = 'ch_groups', group = 'lasts' ))

    itemlist.append(item.clone( title = 'Películas/Series:', action = '', text_color='springgreen' ))
    itemlist.append(item.clone( title = ' - Canales con temática Clásica', action = 'ch_groups', group = 'classic' ))
    itemlist.append(item.clone( title = ' - Canales que pueden contener enlaces Torrents', action = 'ch_groups', group = 'torrents' ))
    itemlist.append(item.clone( title = ' - Canales con Rankings (Más vistas, Más valoradas, etc.)', action = 'ch_groups', group = 'rankings' ))
    itemlist.append(item.clone( title = ' - Canales con Vídeos en Versión Original y/ó Subtitulada', action = 'ch_groups', group = 'vos' ))

    itemlist.append(item.clone( title = 'Películas:', action = '', text_color='cyan' ))
    itemlist.append(item.clone( title = ' - Canales por Idiomas', action = 'ch_groups', group = 'languages' ))
    itemlist.append(item.clone( title = ' - Canales por Años', action = 'ch_groups', group = 'years' ))
    itemlist.append(item.clone( title = ' - Canales con Épocas', action = 'ch_groups', group = 'epochs' ))
    itemlist.append(item.clone( title = ' - Canales por Países', action = 'ch_groups', group = 'countries' ))
    itemlist.append(item.clone( title = ' - Canales por Calidades', action = 'ch_groups', group = 'qualityes' ))

    if not config.get_setting('descartar_anime', default=True):
        itemlist.append(item.clone( title = 'Anime:', action = '', text_color='pink' ))
        itemlist.append(item.clone( title = ' - Canales con contenido Anime', action = 'ch_groups', group = 'anime' ))

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    if not descartar_xxx:
        itemlist.append(item.clone( title = 'Adultos (+18):', action = '', text_color='red' ))
        itemlist.append(item.clone( title = ' - Canales que pueden contener temática para Adultos', action = 'ch_groups', group = 'adults' ))

    itemlist.append(item.clone( title = 'Especiales:', action = '', text_color='moccasin' ))
    itemlist.append(item.clone( title = ' - Canales con Categorias', action = 'ch_groups', group = 'categories' ))
    itemlist.append(item.clone( title = ' - Canales con Intérpretes', action = 'ch_groups', group = 'stars' ))
    itemlist.append(item.clone( title = ' - Canales con Directores/as', action = 'ch_groups', group = 'directors' ))

    itemlist.append(item.clone( title = 'Diversos:', action = '', text_color='fuchsia' ))
    itemlist.append(item.clone( title = ' - Canales con Productoras, Plataformas, y/ó Estudios', action = 'ch_groups', group = 'producers' ))
    itemlist.append(item.clone( title = ' - Canales con Listas, Sagas, Colecciones, y/ó Otros', action = 'ch_groups', group = 'lists' ))
    itemlist.append(item.clone( title = ' - Canales con Vídeos en 3D', action = 'ch_groups', group = '3d' ))

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
    elif group == 'epochs':
         search_type = 'movie'
    elif item.group == 'countries':
         accion = 'paises'
         search_type = 'movie'
    elif item.group == 'qualityes':
         accion = 'calidades'
         search_type = 'movie'

    elif item.group == 'categories': accion = 'categorias'

    color_preferidos = config.get_setting('channels_list_prefe_color')

    canales = []
    filtros = {}

    ch_list = channeltools.get_channels_list(filtros=filtros)
    for ch in ch_list:
        if ch['status'] == -1: continue

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

        color = color_preferidos if ch['status'] == 1 else 'white' if ch['status'] == 0 else 'gray'

        plot = ''
        plot += '[' + ', '.join([config.get_localized_category(ct) for ct in ch['categories']]) + '][CR]'
        plot += '[' + ', '.join([idioma_canal(lg) for lg in ch['language']]) + ']'
        if ch['notes'] != '': plot += '[CR][CR]' + ch['notes']

        titulo = ch['name']
        if ch['status'] == -1: titulo += ' (desactivado)'

        itemlist.append(Item( channel=ch['id'], action=action, title=titulo, text_color=color, plot = plot,
                              thumbnail=ch['thumbnail'], category=ch['name'], search_type = search_type))

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
                itemlist.append(Item( channel='search', action='search', search_type='all', title='- Buscar solo en los canales de este grupo ...',
                                      only_channels_group = canales, thumbnail=config.get_thumb('search'), text_color='plum' ))

    return sorted(itemlist, key=lambda it: it.title)

def idioma_canal(lang):
    idiomas = { 'cast':'Castellano', 'lat':'Latino', 'eng':'Inglés', 'por':'Portugués', 'vo':'VO', 'vose':'VOSE', 'vos':'VOS', 'cat':'Català' }
    return idiomas[lang] if lang in idiomas else lang

