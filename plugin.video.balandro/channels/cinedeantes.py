# -*- coding: utf-8 -*-

from platformcode import logger
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://cinedeantes2.weebly.com'

perpage = 20
perpeli = 10


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Novedades', action = 'news', url = host ))

    itemlist.append(item.clone ( title = 'Joyas del cine', action = 'list_all', url = host + '/joyas-del-cine.html' ))

    itemlist.append(item.clone ( title = 'Por saga', action = 'pelis', url = host, grupo = 'sagas' ))
    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone ( title = 'Por categoría', action = 'pelis', url = host, grupo = 'temas' ))
    itemlist.append(item.clone ( title = 'Por interés', action = 'pelis', url = host, grupo = 'desta' ))

    itemlist.append(item.clone ( title = 'Por actor', action = 'pelis', url = host, grupo = 'actor' ))
    itemlist.append(item.clone ( title = 'Por actriz', action = 'pelis', url = host, grupo = 'actri' ))
    itemlist.append(item.clone ( title = 'Por dirección', action = 'pelis', url = host, grupo = 'direc' ))

    itemlist.append(item.clone ( title = 'Por agrupación (A - Z)', action = 'alfab' ))

    itemlist.append(item.clone ( title = 'Buscar agrupación ...', action = 'search', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Artes marciales', action = 'list_all', url = host + '/artes-marciales.html' ))
    itemlist.append(item.clone ( title = 'Aventuras', action = 'pelis', url = host, filtro_search = 'AVENTURAS' ))

    itemlist.append(item.clone ( title = 'Bélicas (primera guerra)', action = 'list_all', url = host + '/primera-guerra.html' ))
    itemlist.append(item.clone ( title = 'Bélicas (guerra de corea)', action = 'list_all', url = host + '/guerra-corea.html' ))
    itemlist.append(item.clone ( title = 'Bélicas (guerra de vietnam)', action = 'list_all', url = host + '/vietnam.html' ))
    itemlist.append(item.clone ( title = 'Bélicas (acciones bélicas)', action = 'list_all', url = host + '/acciones-beacutelicas.html' ))

    itemlist.append(item.clone ( title = 'Cine argentino', action = 'list_all', url = host + '/cine-argentino.html' ))
    itemlist.append(item.clone ( title = 'Cine asiático', action = 'list_all', url = host + '/cine-asiaacutetico.html' ))
    itemlist.append(item.clone ( title = 'Cine británico', action = 'pelis', url = host, filtro_search = 'CINE BRIT&Aacute;NICO' ))
    itemlist.append(item.clone ( title = 'Cine clásico', action = 'pelis', url = host, filtro_search = 'CL&Aacute;SICO' ))
    itemlist.append(item.clone ( title = 'Cine de acción', action = 'pelis', url = host, filtro_search = 'CINE DE ACCI&Oacute;N' ))
    itemlist.append(item.clone ( title = 'Cine de romanos', action = 'list_all', url = host + '/cine-romanos.html' ))
    itemlist.append(item.clone ( title = 'Cine de terror', action = 'pelis', url = host, filtro_search = 'CINE DE TERROR' ))
    itemlist.append(item.clone ( title = 'Cine español', action = 'pelis', url = host, filtro_search = 'CINE ESPA&Ntilde;OL' ))
    itemlist.append(item.clone ( title = 'Cine francés', action = 'pelis', url = host, filtro_search = 'CINE FRANC&Eacute;S' ))
    itemlist.append(item.clone ( title = 'Cine infantil', action = 'pelis', url = host, filtro_search = 'CINE INFANTIL' ))
    itemlist.append(item.clone ( title = 'Cine italiano', action = 'pelis', url = host, filtro_search = 'CINE ITALIANO' ))
    itemlist.append(item.clone ( title = 'Cine latino', action = 'list_all', url = host + '/cine-latino.html' ))
    itemlist.append(item.clone ( title = 'Cine mexicano', action = 'list_all', url = host + '/cine-mejicano.html' ))
    itemlist.append(item.clone ( title = 'Cine mudo', action = 'pelis', url = host, filtro_search = 'CINE MUDO' ))
    itemlist.append(item.clone ( title = 'Cine musical', action = 'pelis', url = host, filtro_search = 'MUSICAL' ))
    itemlist.append(item.clone ( title = 'Cine negro', action = 'pelis', url = host, filtro_search = 'CINE NEGRO' ))
    itemlist.append(item.clone ( title = 'Cine religioso', action = 'list_all', url = host + '/cine-religioso.html' ))
    itemlist.append(item.clone ( title = 'Cien ruso', action = 'list_all', url = host + '/cine-ruso.html' ))

    itemlist.append(item.clone ( title = 'Comedias', action = 'pelis', url = host, filtro_search = 'COMEDIAS' ))
    itemlist.append(item.clone ( title = 'Ciencia ficción', action = 'pelis', url = host, filtro_search = 'CIENCIA-FICCI&Oacute;N' ))
    itemlist.append(item.clone ( title = 'Espionaje', action = 'pelis', url = host, filtro_search = 'ESPIONAJE' ))
    itemlist.append(item.clone ( title = 'Intriga', action = 'pelis', url = host, filtro_search = 'INTRIGA' ))
    itemlist.append(item.clone ( title = 'Peliculas Vose', action = 'pelis', url = host, filtro_search = 'PEL&Iacute;CULAS V.O.S.E.' ))
    itemlist.append(item.clone ( title = 'Peplum', action = 'pelis', url = host, filtro_search = 'PEPLUM' ))
    itemlist.append(item.clone ( title = 'Westerns', action = 'pelis', url = host, filtro_search = 'WESTERN' ))

    return itemlist


def alfab(item):
    logger.info()
    itemlist = []

    for letra in 'abcdefghijklmnopqrstuvwxyz#':
        itemlist.append(item.clone ( title = letra.upper(), url = host, action = 'pelis', filtro_search = letra ))

    return itemlist


def news(item):
    logger.info()
    itemlist = []

    sort_news = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(host).data

    block_esp = scrapertools.find_single_match(data, '<h2 class="wsite-content-title"><font color="#a88d2e">.*?especial(.*?)>NOVEDADES DE')
    block_nov = scrapertools.find_single_match(data, '>NOVEDADES DE.*?(.*?)>ENLACE AL GRUPO LA TAQUILLA EN FACEBOOK')
    bloque = block_esp + block_nov

    slides = scrapertools.find_multiple_matches(bloque, '<div><div style="height:20px;overflow:hidden"></div>(.*?)<div style="height:20px;overflow:hidden"></div>')

    i = 0

    for slide in slides:
        matches = scrapertools.find_multiple_matches(str(slide), '{"url":(.*?)},')

        for match in matches:
            title = scrapertools.find_single_match(match, '"caption":"(.*?)"').strip()

            if not title: continue

            if 'novedades' in title.lower(): continue
            elif 'cuarentena' in title.lower(): continue

            if 'º' in title:
               if 'comedia ' in title.lower(): title =  title.replace('COMEDIA ', 'COMEDIAS ').replace('Comedia ', 'Comedias ')
            elif 'saga ' in title.lower():
              if 'AÑOS' in title: pass
              title =  title.replace('Saga ', '').replace('SAGA ', '')

            name = title

            title = title.replace('Á', 'á').replace('É', 'é').replace('Í', 'í').replace('Ó', 'ó').replace('Ú', 'ú').replace('Ñ', 'ñ')
            title = title.lower()
            title = title.capitalize()

            thumb = scrapertools.find_single_match(match, '"(.*?)"')
            thumb = host + '/uploads/' + thumb

            i +=1

            sort_news.append([thumb, title, name])

    if not i == 0:
       num_matches = i -1
       desde = item.page * perpage
       hasta = desde + perpage

       sort_news = sorted(sort_news, key=lambda x: x[1])

       for thumb, title, name in sort_news[desde:hasta]:
           title = title.replace('º', 'ª')

           if 'º' in name:
              grupo = 'temas'

              name = name.split('º')[0]
              if 'ACCIÓN' in name: name = name.replace('ACCIÓN', 'ACCI&Oacute;N')
              elif '-FICCIÓN' in name: name = name.replace('-FICCIÓN', '-FICCI&Oacute;N')
              elif 'BRITÁNICO' in name: name = name.replace('BRITÁNICO', 'BRIT&Aacute;NICO')
              elif 'ESPAÑOL' in name: name = name.replace('ESPAÑOL', 'ESPA&Ntilde;OL')
              elif 'FRANCÉS' in name: name = name.replace('FRANCÉS', 'FRANC&Eacute;S')
              elif 'CLÁSICO' in name: name = name.replace('CLÁSICO', 'CL&Aacute;SICO')
              elif 'BÉLICAS' in name: name = name.replace('BÉLICAS', 'B&Eacute;LICAS')
              elif 'AÑOS' in name: name = name.replace('AÑOS', 'A&Ntilde;OS')
           else:
              grupo = ''

              if name == 'AÑOS 80-90': name = name.replace('AÑOS 80-90', 'SAGAS A&Ntilde;OS 80 Y 90')
              elif name == 'años 80-90': name = name.replace('años 80-90', 'SAGAS A&Ntilde;OS 80 Y 90')
              elif name == 'Paco Martínez Soria': name = name.replace('Paco Martínez Soria', 'PACO MART&Iacute;NEZ SORIA')
              elif name == 'Sissi': name = name.replace('Sissi', 'SISSI')
              elif name == 'JOAN CROWFORD': name = name.replace('JOAN CROWFORD', 'JOAN CRAWFORD')

           if '/' in name: name = name.split('/')[0]
           elif '(' in name: name = name.split('(')[0]

           itemlist.append(item.clone( action = 'pelis', title = title, url = host, thumbnail = thumb, grupo = grupo, filtro_search = name, page = 0 ))

       if i > perpage:
          if num_matches > hasta:
             next_page = item.page + 1
             itemlist.append(item.clone( title = '>> Página siguiente', page = next_page, action = 'news', text_color='coral' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<div id=".*?class="wcustomhtml".*?src="(.*?)"')

    cover = scrapertools.find_single_match(data, '<div><div class="wsite-image wsite-image-border-none ".*?<img src="([^"]+)"')
    if cover.startswith("/") == True: cover = host + cover

    num_matches = len(matches)
    desde = item.page * perpeli
    hasta = desde + perpeli

    order = 0

    for match in matches[desde:hasta]:
        if match.startswith('//') == True: url = 'https:' + match
        else: url = match

        data_thumb = httptools.downloadpage(url).data

        thumb = scrapertools.find_single_match(data_thumb, '<img src="([^"]+)"')
        thumb = thumb.replace('&amp;', '&')

        if not thumb: thumb = cover

        title = scrapertools.find_single_match(data_thumb, 'class="vid-card_n">(.*?)</span>')
        title = title.replace('(EEEE) p30', '').replace('(EEE) p20', '').replace('(EE)', '').replace('(C)', '').replace('(c)', '').strip()

        year = '-'

        try:
           name = title.split(" (")[0]
           year = title.split(" (")[1]

           if ')' in year: year = year.split(")")[0]
           elif '-' in year: year = year.split("-")[0]

           if year: title = name
        except:
            name = title

        if not title:
           order += 1
           title = '¿ Pelicula  ' + str(order) + ' ?'
        else:
           if title.endswith(") 0") == True: title = title.replace(' 0', '')
           elif title.endswith(") 1") == True: title = title.replace(' 1', '')
           elif title.endswith(") 2") == True: title = title.replace(' 2', '')
           elif title.endswith(") 3") == True: title = title.replace(' 3', '')
           elif title.endswith(") 4") == True: title = title.replace(' 4', '')
           elif title.endswith(") 5") == True: title = title.replace(' 5', '')
           elif title.endswith(") 6") == True: title = title.replace(' 6', '')
           elif title.endswith(") 7") == True: title = title.replace(' 7', '')
           elif title.endswith(") 8") == True: title = title.replace(' 8', '')
           elif title.endswith(") 9") == True: title = title.replace(' 9', '')

        lang = 'Esp'
        if ' vose' in title.lower() or ' v.o.s.e.' in title.lower(): lang = 'Vose'

        itemlist.append(item.clone( action='findvideos', url = url, title = title, language = lang, thumbnail = thumb,
                                    contentType = 'movie', contentTitle = name, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if matches:
       if num_matches > hasta:
           next_page = item.page + 1
           itemlist.append(item.clone( title = '>> Página siguiente', page = next_page, action = 'list_all', text_color='coral' ))

    return itemlist


def pelis(item):
    logger.info()
    itemlist = []

    sort_pelis = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(host).data

    bloque = scrapertools.find_single_match(data, '<li id="active" class="wsite-menu-item-wrap">(.*?)</div><!-- end header-wrap -->')

    if item.grupo:
       if item.grupo == 'sagas': bloque = scrapertools.find_single_match(data, '/s-a-g-a-s.html(.*?)/humor.html')
       elif item.grupo == 'actor': bloque = scrapertools.find_single_match(data, '/actores.html(.*?)/actrices.html')
       elif item.grupo == 'actri': bloque = scrapertools.find_single_match(data, '/actrices.html(.*?)/s-a-g-a-s.html')
       elif item.grupo == 'direc': bloque = scrapertools.find_single_match(data, '/directores.html(.*?)/actores.html')
       elif item.grupo == 'desta': bloque = scrapertools.find_single_match(data, '/humor.html(.*?)</div><!-- end header-wrap -->')

    if item.filtro_search: matches = scrapertools.find_multiple_matches(bloque, '<li id="(.*?)</a>')
    else:
       if not item.grupo == 'temas': matches = scrapertools.find_multiple_matches(bloque, '<li id=(.*?)</li>')
       else: matches = scrapertools.find_multiple_matches(bloque, '<li id="(.*?)</a>')

    i = 0

    for match in matches:
        if '<span class="wsite-menu-arrow">' in match:
           if not 'SAGAS A&Ntilde;OS 80 Y 90' in match: continue

        if '<li id="wsite-nav-' in match:
           match = match + '</li>'
           match = scrapertools.find_single_match(match, '<li id="wsite-nav-(.*?)</li>')

        url = scrapertools.find_single_match(match, 'href="([^"]+)"')

        if not url: continue

        title = scrapertools.find_single_match(match, 'class="wsite-menu-title">(.*?)</span>').strip()
        if not title: title = scrapertools.find_single_match(match, 'class="wsite-menu-item".*?>(.*?)</a>').strip()

        if item.filtro_search:
           if not title:
              if 'class="wsite-menu-item"' in match:
                 match_mod = match 
                 if not '</a>' in match_mod: match_mod = match_mod + '</a>'
                 title = scrapertools.find_single_match(match_mod, 'class="wsite-menu-item".*?>(.*?)</a>').strip()
                 if not title: title = scrapertools.find_single_match(match_mod, 'class="wsite-menu-item".*?>(.*?)</span>').strip()

        if not title: continue

        if title == 'Blog': continue
        elif title == 'AVENTURAS': continue
        elif title == 'BÉLICAS': continue
        elif title == 'CIENCIA-FICCIÓN': continue
        elif title == 'CINE BRITÁNICO': continue
        elif title == 'CINE DE ACCIÓN': continue
        elif title == 'CINE DE TERROR': continue
        elif title == 'CINE ESPAÑOL': continue
        elif title == 'CINE INFANTIL': continue
        elif title == 'CINE ITALIANO': continue
        elif title == 'CINE MUSICAL': continue
        elif title == 'CINE MUDO': continue
        elif title == 'CINE NEGRO': continue
        elif title == 'COMEDIAS': continue
        elif title == 'ESPIONAJE': continue
        elif title == 'HUMOR': continue
        elif title == 'INTRIGA': continue
        elif title == 'PELÍCULAS V.O.S.E.': continue
        elif title == 'PEPLUM': continue
        elif title == 'SEGUNDA GUERRA': continue
        elif title == 'SPAGHETTI WESTERN': continue
        elif title == 'WESTERNS': continue
        elif title == 'C I C L O S': continue
        elif title == 'S A G A S': continue

        url = host + url

        if 'WESTERN 6 ' in title: title = title.replace('WESTERN 6 ', 'WESTERN 6&ordm; ')
        elif title == 'A L I E N': title = title.replace('A L I E N', 'ALIEN')
        elif title == 'A S T E R I X': title = title.replace('A S T E R I X', 'ASTERIX')
        elif title == 'D R &Aacute; C U L A': title = title.replace('D R &Aacute; C U L A', 'DRACULA')
        elif title == 'P A S O L I N I': title = title.replace('P A S O L I N I', 'PASOLINI')
        elif title == 'R A M B O': title = title.replace('R A M B O', 'RAMBO')
        elif title == 'S A N D O K A N': title = title.replace('S A N D O K A N', 'SANDOKAN')
        elif title == 'S I M B A D': title = title.replace('S I M B A D', 'SIMBAD')
        elif title == 'S I S S I': title = title.replace('S I S S I', 'SISSI')
        elif title == 'T A R Z &Aacute; N': title = title.replace('T A R Z &Aacute; N', 'TARZAN')

        if item.filtro_search:
           buscado = item.filtro_search.lower().strip()
           titulo = title.lower().strip()

           if len(buscado) == 1:
              letra_titulo = titulo[0]
              if not letra_titulo == buscado:
                 if not buscado == '#': continue
                 if letra_titulo in '0123456789': pass
                 else: continue
           elif not buscado in titulo: continue

        else:
           if not item.grupo == 'temas':
              if '&ordm;' in title: continue
           else:
              if not '&ordm;' in title: continue

        title = title.replace('&ordm;', 'ª').replace('Ó', 'ó').replace('Á', 'á')
        title = title.lower()
        title = title.capitalize()

        if 'Cine  de' in title: title = title.replace('Cine  de', 'Cine de')
        elif 'Pel&iacute;culas  v' in title: title = title.replace('Pel&iacute;culas  v', 'Pel&iacute;culas v')

        if item.grupo == 'desta':
           if title == '007 - james bond': continue
           elif title == 'Artes marciales': continue
           elif title == 'Aventuras': continue
           elif title == 'Primera guerra': continue
           elif title == 'Guerra corea': continue
           elif title == 'Vietnam': continue
           elif title == 'Acciones b&eacute;licas': continue
           elif title == 'Cine argentino': continue
           elif title == 'Cine asiático': continue
           elif title == 'Cine británico': continue
           elif title == 'Cine clásico': continue
           elif title == 'Cine de acción': continue
           elif title == 'Cine romanos': continue
           elif title == 'Cine de terror': continue
           elif title == 'Cine español': continue
           elif title == 'Cine francés': continue
           elif title == 'Cine infantil': continue
           elif title == 'Cine italiano': continue
           elif title == 'Cine latino': continue
           elif title == 'Cine mejicano': continue
           elif title == 'Cine mudo': continue
           elif title == 'Cine musical': continue
           elif title == 'Cine negro': continue
           elif title == 'Cine religioso': continue
           elif title == 'Cine ruso': continue
           elif title == 'Comedias': continue
           elif title == 'Ciencia ficción': continue
           elif title == 'Espionaje': continue
           elif title == 'Intriga': continue
           elif title == 'Joyas del cine': continue
           elif title == 'Peliculas v.o.s.e.': continue
           elif title == 'Peplum': continue
           elif title == 'Westerns': continue

        if 'ª' in title: title = title.replace('ª', 'ª - L')

        i +=1

        sort_pelis.append([url, title])

    if not i == 0:
       num_matches = i -1
       desde = item.page * perpage
       hasta = desde + perpage

       sort_pelis = sorted(sort_pelis, key = lambda x: x[1])

       for url, title in sort_pelis[desde:hasta]:
           itemlist.append(item.clone( action = 'list_all', title = title, url = url, page = 0 ))

       if not item.filtro_search:
          if i > perpage:
             if num_matches > hasta:
                next_page = item.page + 1
                itemlist.append(item.clone( title = '>> Página siguiente', page = next_page, action = 'pelis', text_color='coral' ))

    return itemlist

# Por si viene del menu de Agrupaciones
def categorias(item):
    logger.info()

    item.url = host
    item.grupo = 'temas'
    return pelis(item)


def findvideos(item):
    logger.info()
    itemlist = []

    servidor = servertools.get_server_from_url(item.url)

    if servidor and servidor != 'directo':
       url = servertools.normalize_url(servidor, item.url)

       itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = item.language ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.url = host
       item.filtro_search = texto
       return pelis(item)
    except:
       import sys
       for line in sys.exc_info():
           logger.error("%s" % line)
       return []
