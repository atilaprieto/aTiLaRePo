# -*- coding: utf-8 -*-

import os, sys

from platformcode import config, logger, platformtools
from core import filetools
from core.item import Item

_foro = "[COLOR plum][B][I] balandro.tk [/I][/B][/COLOR]"
_telegram = "[COLOR lightblue][B][I] @balandro_asesor [/I][/B][/COLOR]"


if sys.version_info[0] >= 3:
    import xbmcvfs
    translatePath = xbmcvfs.translatePath
else:
    import xbmc
    translatePath = xbmc.translatePath


def mainlist(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)
    descartar_anime = config.get_setting('descartar_anime', default=False)

    itemlist.append(item.clone( action='', title= 'Contacto:', text_color='blue', folder=False ))
    itemlist.append(item.clone( action='', title= ' - Foro ' + _foro + ' Novedades, Sugerencias, Aportaciones, etc.', folder=False ))
    itemlist.append(item.clone( action='', title= ' - Telegram ' + _telegram + ' Asesoramiento, Dudas, Ayuda, etc.', folder=False ))

    itemlist.append(item.clone( action='', title= 'Uso:', text_color='chartreuse', folder=False ))
    itemlist.append(item.clone( action='show_channels_list', title= ' - Qué canales están disponibles', folder=False, thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( action='show_channels_list', title= ' - Qué canales están inactivos', no_active = True, folder=False, thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( action='show_help_tips', title= ' - Trucos y consejos varios', folder=False ))
    itemlist.append(item.clone( action='show_help_use', title= ' - Ejemplos de niveles de uso', folder=False ))
    itemlist.append(item.clone( action='show_help_faq', title= ' - FAQS - Preguntas y respuestas', folder=False ))
    itemlist.append(item.clone( action='show_help_settings', title= ' - Notas sobre algunos parámetros de la configuración', folder=False ))

    itemlist.append(item.clone( action='', title= 'Proxies:', text_color='red', folder=False ))
    itemlist.append(item.clone( action='channels_with_proxies', title= ' - Qué canales pueden usar proxies', folder=False, thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( action='show_help_proxies', title= ' - Información uso de proxies', folder=False ))

    itemlist.append(item.clone( action='', title= 'Torrents:', text_color='moccasin', folder=False ))
    itemlist.append(item.clone( action='show_clients_torrent', title= ' - Clientes externos torrent soportados', folder=False, thumbnail=config.get_thumb('cloud') ))
    itemlist.append(item.clone( action='channels_only_torrents', title= ' - Qué canales pueden contener archivos torrent', folder=False, thumbnail=config.get_thumb('cloud') ))
    itemlist.append(item.clone( action='show_help_torrents', title= ' - ¿ Dónde obtener los add-ons para torrents ?', folder=False, thumbnail=config.get_thumb('cloud') ))

    itemlist.append(item.clone( action='', title='Buscar:', text_color='cyan', folder=False ))
    itemlist.append(item.clone( channel='search', action='show_help', title = ' - Información sobre búsquedas', folder=False, thumbnail=config.get_thumb('search') ))
    itemlist.append(item.clone( channel='tmdblists', action='show_help', title= ' - Información búsquedas y listas en TMDB', folder=False, thumbnail=config.get_thumb('search') ))
    itemlist.append(item.clone( channel='filters', title = ' - Excluir canales en las búsquedas', action = 'mainlist', thumbnail=config.get_thumb('stack') ))

    presentar = True
    if descartar_xxx:
        if descartar_anime: presentar = False

    if presentar:
        itemlist.append(item.clone( action='', title= 'Parental:', text_color='orangered', folder=False ))

        if not descartar_anime:
            itemlist.append(item.clone( action='channels_only_animes', title= ' - Qué canales pueden tener contenido de animes', folder=False, thumbnail=config.get_thumb('anime') ))

        if not descartar_xxx:
            itemlist.append(item.clone( action='channels_only_adults', title= ' - Qué canales pueden tener contenido para adultos', folder=False, thumbnail=config.get_thumb('adults') ))
            itemlist.append(item.clone( action='show_help_adults', title= ' - Informacion Control parental (+18)', folder=False ))

    itemlist.append(item.clone( action='', title='Preferidos:', text_color='springgreen', folder=False ))
    itemlist.append(item.clone( action='show_help_tracking', title= ' - Cómo funciona', folder=False, thumbnail=config.get_thumb('videolibrary') ))
    itemlist.append(item.clone( action='show_help_tracking_update', title= ' - Búsqueda automática de nuevos episodios', folder=False, thumbnail=config.get_thumb('videolibrary') ))

    itemlist.append(item.clone( action='', title='Actualizar:', text_color='salmon', folder=False ))
    itemlist.append(item.clone( channel='actions', title= ' - Comprobar últimas actualizaciones tipo Fix', action = 'check_addon_updates', folder=False, thumbnail=config.get_thumb('download') ))
    itemlist.append(item.clone( channel='actions', title= ' - Forzar todas las actualizaciones tipo Fix', action = 'check_addon_updates_force', folder=False, thumbnail=config.get_thumb('download') ))
    itemlist.append(item.clone( action='show_last_fix', title= ' - Información último fix instalado', folder=False, thumbnail=config.get_thumb('news') ))

    itemlist.append(item.clone( action='', title='Servidores:', text_color='gold', folder=False ))
    itemlist.append(item.clone( action='show_servers_list', title= ' - Qué servidores están disponibles', tipo = 'activos', folder=False, thumbnail=config.get_thumb('bolt') ))
    itemlist.append(item.clone( action='show_servers_list', title= ' - Qué servidores están inactivos', tipo = 'inactivos', folder=False, thumbnail=config.get_thumb('bolt') ))
    itemlist.append(item.clone( action='show_servers_list', title= ' - Lista de todos los servidores', tipo = 'all', folder=False, thumbnail=config.get_thumb('bolt') ))

    itemlist.append(item.clone( action='', title= 'Sistema:', text_color='yellow', folder=False ))
    itemlist.append(item.clone( action='show_test', title= ' - Test status del sistema', folder=False, thumbnail=config.get_thumb('computer') ))
    itemlist.append(item.clone( action='show_sets', title= ' - Visualizar sus ajustes personalizados', folder=False, thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( action='show_cook', title= ' - Visualizar su fichero de cookies', folder=False, thumbnail=config.get_thumb('folder') ))
    itemlist.append(item.clone( channel='actions', title= ' - Configuración', action = 'open_settings', folder=False, thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( action='', title= 'Media Center:', text_color='pink', folder=False ))
    itemlist.append(item.clone( action='show_log', title= ' - Visualizar el fichero log de su Media Center', folder=False, thumbnail=config.get_thumb('computer') ))
    itemlist.append(item.clone( action='copy_log', title= ' - Obtener una copia del fichero log de su Media Center', folder=False, thumbnail=config.get_thumb('computer') ))
    itemlist.append(item.clone( action='show_advs', title= ' - Visualizar el fichero advancedsettings de su Media Center', folder=False, thumbnail=config.get_thumb('keyboard') ))

    itemlist.append(item.clone( action='', title='Desarrollo:', text_color='fuchsia', folder=False ))
    itemlist.append(item.clone( action='show_version', title= ' - Información versión', folder=False, thumbnail=config.get_thumb('news') ))
    itemlist.append(item.clone( action='show_changelog', title= ' - Historial de cambios', folder=False, thumbnail=config.get_thumb('news') ))
    itemlist.append(item.clone( action='show_dev_notes', title= ' - Notas para developers', folder=False, thumbnail=config.get_thumb('tools') ))
    itemlist.append(item.clone( action='show_license', title= ' - Licencia (Gnu Gpl v3)', folder=False, thumbnail=config.get_thumb('megaphone') ))
    itemlist.append(item.clone( action='show_legalidad', title= ' - Legalidad', folder=False, thumbnail=config.get_thumb('megaphone') ))

    return itemlist


def channels_only_animes(item):
    logger.info()

    from modules import filters

    filters.only_animes(item)

def channels_only_adults(item):
    logger.info()

    from modules import filters

    filters.only_adults(item)

def show_channels_list(item):
    logger.info()

    from modules import filters

    filters.show_channels_list(item)

def channels_with_proxies(item):
    logger.info()

    from modules import filters

    filters.with_proxies(item)

def channels_no_actives(item):
    logger.info()

    from modules import filters

    filters.no_actives(item)

def channels_prefered(item):
    logger.info()

    from modules import filters

    filters.only_prefered(item)

def channels_only_torrents(item):
    logger.info()

    from modules import filters

    filters.only_torrents(item)


def show_clients_torrent(item):
    logger.info()

    from modules import filters

    filters.show_clients_torrent(item)

def show_servers_list(item):
    logger.info()

    from modules import filters

    if not item.tipo: # por si venimos de config
        item.tipo = 'activos'

    filters.show_servers_list(item)


# Diálogos para mostrar info de Ayuda
def show_help_settings(item):
    logger.info()

    txt = '*) Las opciones para los [COLOR gold]listados de canales[/COLOR] se usan si marcas canales como preferidos o desactivados.'
    txt += ' Esto lo puedes hacer desde el menú contextual en los listados de canales.'

    txt += '[CR][CR]'
    txt += '*) En "Búsquedas" el parámetro "[COLOR gold]Resultados previsualizados por canal[/COLOR]" sirve para limitar el número de coincidencias que se muestran en la pantalla de búsqueda global.'
    txt += ' Es para que no salga un listado demasiado largo ya que algunos canales son más sensibles que otros y pueden devolver bastantes resultados.'
    txt += ' Pero de todas maneras se puede acceder al listado de todos los resultados de cada canal concreto.'
    txt += ' Dispones de más parámetros personalizables en la configuración "Buscar".'

    txt += '[CR][CR]'
    txt += '*) En "Reproducción" se puede activar Autoplay para no tener que seleccionar un servidor para reproducir.'
    txt += ' Si hay algún canal para el que quieras desactivar el autoplay puedes indicarlo en la configuración "Play".'

    txt += '[CR][CR]'
    txt += '*) En "Reproducción" los parámetros para ordenar/filtrar los enlaces [COLOR gold]por idioma[/COLOR] permiten indicar nuestras preferencias de idiomas.'
    txt += ' Entre Español, Latino y Versión Original elije el orden que prefieres, o descarta alguno de ellos si no te interesa.'
    txt += ' Todo ello puedes personalizarlo en la configuración "Play".'

    txt += '[CR][CR]'
    txt += '*) En "Reproducción" los parámetros para ordenar los enlaces [COLOR gold]por calidad[/COLOR] permiten mostrar antes los de más calidad en lugar de mostrarlos según el orden que tienen en la web.'
    txt += ' Algunos canales tienen valores fiables de calidad pero otros no, depende de cada web.'
    txt += ' Todo ello puedes personalizarlo en la configuración "Play".'

    txt += '[CR][CR]'
    txt += '*) En "Reproducción" los parámetros para ordenar/filtrar los enlaces [COLOR gold]por servidores[/COLOR] permiten hacer algunos ajustes en función de los servers.'
    txt += ' Si no quieres que te salgan enlaces de ciertos servidores, escríbelos en "descartados" (ej: torrent,mega).'
    txt += ' Y si quieres priorizar algunos servidores escríbelos en "preferentes" (ej: torrent,mega), o al revés en "última opción" (ej: torrent,mega).'
    txt += ' Para modificar estas opciones necesitas saber qué servidores te funcionan mejor y peor, en caso de duda no hace falta que lo modifiques.'
    txt += ' Todo ello puedes personalizarlo en la configuración "Play".'

    txt += '[CR][CR]'
    txt += '*) Una opción que puede provocar una demora en los tiempos de respuesta es en configuración "TMDB" si se activa "[COLOR gold]buscar información extendida[/COLOR]".'
    txt += ' Esto provoca que los listados de películas y series de todos los canales tarden más en mostrarse ya que se hace una segunda llamada a TMDB para intentar recuperar más datos.'

    txt += '[CR][CR]'
    txt += '*) En "TMDB" se pueden desactivar las "[COLOR gold]llamadas a TMDB en los listados[/COLOR]".'
    txt += ' Esto provoca que los listados de películas y series de todos los canales tarden menos en mostrarse pero en la mayoría de casos no tendrán información como la sinopsis y las carátulas serán de baja calidad.'
    txt += ' Puede ser útil desactivarlo temporalmente en casos dónde alguna película/serie no se identifica correctamente en tmdb y se quieran ver los datos originales de la web.'

    txt += '[CR][CR]'
    txt += '*) Exiten más parámetros en la [COLOR gold]Configuracion[/COLOR] de Balandro,  para tener personalizada su ejecución.'
    txt += ' Divididos en agruaciones [COLOR gold]Canales, Play, Proxies, Torrents, Buscar, Preferidos, Descargas, Actualizar, etc.[/COLOR].'

    platformtools.dialog_textviewer('Notas sobre algunos parámetros de la configuración', txt)


def show_help_tips(item):
    logger.info()

    txt = '*) Es importante usar el [B][COLOR gold]menú contextual[/COLOR][/B] para acceder a acciones que se pueden realizar sobre los elementos de los listados.'
    txt += ' Si dispones de un teclado puedes acceder a él pulsando la tecla C, en dispositivos táctiles manteniendo pulsado un elemento, y en mandos de tv-box manteniendo pulsado el botón de selección.'
    txt += ' Si usas un mando de TV es recomendable configurar una de sus teclas con "ContextMenu".'

    txt += '[CR][CR]'
    txt += '*) En los listados de canales puedes usar el menú contextual para marcarlos como Desactivado/Activo/Preferido.'
    txt += ' De esta manera podrás tener tus [COLOR gold]canales preferidos[/COLOR] al inicio y quitar o mover al final los que no te interesen.'
    txt += ' Los canales desactivados son accesibles pero no forman parte de las búsquedas.'

    txt += '[CR][CR]'
    txt += '*) Si en algún canal encuentras una película/serie que te interesa pero fallan sus enlaces, accede al menú contextual y selecciona'
    txt += ' "[COLOR gold]buscar en otros canales[/COLOR]" para ver si está disponible en algún otro canal.'

    txt += '[CR][CR]'
    txt += '*) Desde cualquier pantalla desplázate hacia el lateral izquierdo para desplegar algunas [COLOR gold]opciones standard de su Media Center[/COLOR].'
    txt += ' Allí tienes siempre un acceso directo a la Configuración del addon y también puedes cambiar el tipo de vista que se aplica a los listados.'
    txt += ' Entre Lista, Cartel, Mays., Muro de información, Lista amplia, Muro, Fanart, escoge como prefieres ver la información.'

    txt += '[CR][CR]'
    txt += '*) Algunos canales de series tienen un listado de [COLOR gold]últimos episodios[/COLOR]. En función de las características de las webs, los enlaces llevan'
    txt += ' a ver el capítulo o a listar las temporadas de la serie. Cuando es posible, desde el enlace se ve el episodio y desde el menú contextual'
    txt += ' se puede acceder a la temporada concreta o la lista de temporadas.'

    txt += '[CR][CR]'
    txt += '*) Para seguir series es recomendable usar la opción [COLOR gold]Preferidos[/COLOR]. Busca la serie que te interese en cualquiera de los canales y desde el menú contextual guárdala.'
    txt += ' Luego ves a "Preferidos" dónde podrás gestionar lo necesario para la serie. Además puedes usar "Buscar en otros canales" y desde el listado de resultados con el menú'
    txt += ' contextual también los puedes guardar y se añadirán a los enlaces que ya tenías. De esta manera tendrás alternativas en diferentes enlaces por si algún día falla alguno o desaparece.'

    platformtools.dialog_textviewer('Trucos y consejos varios', txt)


def show_help_use(item):
    logger.info()

    txt = '[COLOR gold]Nivel 1, casual[/COLOR][CR]'
    txt += 'Accede por ejemplo a Películas o Series desde el menú principal, entra en alguno de los canales y navega por sus diferentes opciones hasta encontrar una película que te interese.'
    txt += ' Al entrar en la película se mostrará un diálogo con diferentes opciones de vídeos encontrados.'
    txt += ' Prueba con el primero y si el enlace es válido empezará a reproducirse. Sino, prueba con alguno de los otros enlaces disponibles.'
    txt += ' Si ninguno funcionara, desde el enlace de la película accede al menú contextual y selecciona "Buscar en otros canales".'

    txt += '[CR][CR][COLOR gold]Nivel 2, directo[/COLOR][CR]'
    txt += 'Si quieres ver una película/serie concreta, accede a "Buscar" desde el menú principal y escribe el título en el buscador.'
    txt += ' Te saldrá una lista con las coincidencias en todos los canales disponibles.'

    txt += '[CR][CR][COLOR gold]Nivel 3, planificador[/COLOR][CR]'
    txt += 'Navega por los diferentes canales y ves apuntando las películas/series que te puedan interesar.'
    txt += ' Para ello accede al menú contextual desde cualquier película/serie y selecciona "Guardar enlace".'
    txt += ' Cuando quieras ver una película/serie, accede a "Preferidos" desde el menú principal dónde estará todo lo guardado.'

    txt += '[CR][CR][COLOR gold]Nivel 4, asegurador[/COLOR][CR]'
    txt += 'Descarga algunas películas para tener listas para ver sin depender de la saturación de la red/servidores en momentos puntuales.'
    txt += ' Desde cualquier película/episodio, tanto en los canales como en "Preferidos", accede al menú contextual y "Descargar vídeo".'
    txt += ' Selecciona alguno de los enlaces igual que cuando se quiere reproducir y empezará la descarga.'
    txt += ' Para ver lo descargado, accede a "Descargas" desde el menú principal.'

    txt += '[CR][CR][COLOR gold]Nivel 5, coleccionista[/COLOR][CR]'
    txt += 'Desde "Preferidos" accede a "Gestionar listas", dónde puedes crear diferentes listas para organizarte las películas y series que te interesen.'
    txt += ' Por ejemplo puedes tener listas para distintos usuarios de Balandro (Padres, Esposa, Hijos, etc.) o de diferentes temáticas, o para guardar lo que ya hayas visto, o para pasar tus recomendaciones a algún amigo, etc.'

    platformtools.dialog_textviewer('Ejemplos de uso de Balandro', txt)


def show_help_faq(item):
    logger.info()

    txt = '[COLOR gold]¿ De dónde viene Balandro ?[/COLOR][CR]'
    txt += 'Balandro es un addon derivado de Pelisalacarta y Alfa, simplificado a nivel interno de código y a nivel funcional para el usuario.'
    txt += ' Puede ser útil en dispositivos poco potentes como las Raspberry Pi u otros TvBox y para usuarios que no se quieran complicar mucho.'
    txt += ' Al ser un addon de tipo navegador, tiene el nombre de un velero ya que balandro era una embarcación ligera y maniobrable, muy apreciada por los piratas.'

    txt += '[CR][CR][COLOR gold]¿ Qué características tiene Balandro ?[/COLOR][CR]'
    txt += 'Principalmente permite acceder a los contenidos de webs con vídeos de películas y series para reproducirlos y/o guardarlos, y'
    txt += ' dispone de unos Preferidos propios dónde poder apuntar todas las Películas y Series que interesen al usuario.'
    txt += ' Se pueden configurar múltiples opciones, por ejemplo la preferencia de idioma, la reproducción automática, los colores para los listados, los servidores preferidos, excluir canales en las búsquedas, etc.'

    txt += '[CR][CR][COLOR gold]¿ Cómo funciona el Autoplay ?[/COLOR][CR]'
    txt += 'Se puede activar la función de reproducción automática desde la configuración del addon.'
    txt += ' Si se activa, al ver una película o episodio se intenta reproducir el primero de los enlaces que funcione, sin mostrarse el diálogo de selección de servidor.'
    txt += ' Los enlaces se intentan secuencialmente en el mismo orden que se vería en el diálogo, por lo que es importante haber establecido las preferencias de idioma, servidores y calidades.'

    txt += '[CR][CR][COLOR gold]¿ En qué orden se muestran los enlaces de servidores ?[/COLOR][CR]'
    txt += 'El orden inicial es por la fecha de los enlaces, para tener al principio los últimos actualizados ya que es más probable que sigan vigentes, aunque en los canales que no lo informan es según el orden que devuelve la web.'
    txt += ' Desde la configuración se puede activar el ordenar por calidades, pero su utilidad va a depender de lo que muestre cada canal y la fiabilidad que tenga.'
    txt += ' A partir de aquí, si hay preferencias de servidores en la configuración, se cambia el orden para mostrar al principio los servidores preferentes y al final los de última opción.'
    txt += ' Y finalmente se agrupan en función de las preferencias de idiomas del usuario.'

    txt += '[CR][CR][COLOR gold]¿ Funcionan los enlaces Torrent ?[/COLOR][CR]'
    txt += 'El addon está preparado para tratarlos usando un gestor de torrents externo, tipo Quasar, Elementum, etc.'
    txt += ' Estos gestores externos torrents no estan incluidos en Balandro y deben Instalarse por separado.'
    txt += ' Además, debe indicarse Obligatoriamente en la configuración de Balandro cual va a ser su gestor de torrents habitual.'

    platformtools.dialog_textviewer('FAQ - Preguntas y respuestas', txt)


def show_help_tracking(item):
    logger.info()

    txt = '[COLOR gold]¿ Cómo se guardan las películas o series ?[/COLOR][CR]'
    txt += 'Desde cualquiera de los canales dónde se listen películas o series, accede al menú contextual y selecciona "Guardar película/serie".'
    txt += ' En el caso de películas es casi instantáneo, y para series puede demorarse unos segundos si tiene muchas temporadas/episodios.'
    txt += ' Para ver y gestionar todo lo que tengas, accede a "Preferidos" desde el menú principal del addon.'
    txt += ' También puedes guardar una temporada o episodios concretos.'

    txt += '[CR][CR][COLOR gold]¿ Qué pasa si una película/serie no está correctamente identificada ?[/COLOR][CR]'
    txt += 'Esto puede suceder cuando la película/serie no está bien escrita en la web de la que procede o si hay varias películas con el mismo título.'
    txt += ' Si no se detecta te saldrá un diálogo para seleccionar entre varias opciones o para cambiar el texto de búsqueda.'
    txt += ' Desde las opciones de configuración puedes activar que se muestre siempre el diálogo de confirmación, para evitar que se detecte incorrectamente.'

    txt += '[CR][CR][COLOR gold]¿ Y si no se puede identificar la película/serie ?[/COLOR][CR]'
    txt += 'Es necesario poder identificar cualquier película/serie en TMDB, sino no se puede guardar.'
    txt += ' Si no existe en [COLOR gold]themoviedb.org[/COLOR] o tiene datos incompletos puedes completar allí la información ya que es un proyecto comunitario y agradecerán tu aportación.'

    txt += '[CR][CR][COLOR gold]¿ Se puede guardar la misma película/serie desde canales diferentes ?[/COLOR][CR]'
    txt += 'Sí, al guardar se apuntan en la base de datos interna los datos propios de la película, serie, temporada o episodio, y también el enlace al canal de dónde se ha guardado.'
    txt += ' De esta manera puedes tener diferentes alternativas por si algún canal fallara o no tuviera enlaces válidos.'
    txt += ' Si tienes enlaces de varios canales, al reproducir podrás escoger en cual intentarlo.'

    txt += '[CR][CR][COLOR gold]¿ Se guardan las marcas de películas/episodios ya vistos ?[/COLOR][CR]'
    txt += 'Sí, su Media Center gestiona automáticamente las marcas de visto/no visto.'
    txt += ' Estas marcas están en la base de datos de su Media Center pero no en las propias de Balandro.'

    txt += '[CR][CR][COLOR gold]¿ Qué pasa si un enlace guardado deja de funcionar ?[/COLOR][CR]'
    txt += 'A veces las webs desaparecen o cambian de estructura y/o de enlaces, y eso provoca que en Preferidos dejen de ser válidos.'
    txt += ' Al acceder a un enlace que da error, se muestra un diálogo para escoger si se quiere "Buscar en otros canales" o "Volver a buscar en el mismo canal".'
    txt += ' Si la web ha dejado de funcionar deberás buscar en otros canales, pero si ha sufrido cambios puedes volver a buscar en ella.'

    txt += '[CR][CR][COLOR gold]¿ Se puede compartir una lista de Preferidos ?[/COLOR][CR]'
    txt += 'De momento puedes hacerlo manualmente. En la carpeta userdata del addon, dentro de "tracking_dbs" están los ficheros [COLOR gold].sqlite[/COLOR] de cada lista que tengas creada.'
    txt += ' Puedes copiar estos ficheros y llevarlos a otros dispositivos.'

    txt += '[CR][CR][COLOR gold]¿ Cómo invertir el orden de los episodios ?[/COLOR][CR]'
    txt += 'Por defecto los episodios dentro de una temporada se muestran en orden ascendente, del primero al último.'
    txt += ' Si prefieres que sea al revés, desde el menú contextual de una temporada selecciona "Invertir el orden de los episodios" y'
    txt += ' tu preferencia quedará guardada para esa temporada.'

    txt += '[CR][CR][COLOR gold]¿ Hay alguna límitación en los episodios a guardar por cada temporada ?[/COLOR][CR]'
    txt += 'Si, no se almacenarán más de 50 episodios por temporada, si fuera necesario, debe gestionar esa serie y/o temporada'
    txt += ' a través de los "favoritos/videoteca genérica" de su Media Center.'

    txt += '[CR][CR][COLOR gold]¿ Cómo integrar los Preferidos en la Videoteca de su Media Center? ?[/COLOR][CR]'
    txt += 'Una alternativa es añadir los Preferidos de Balandro a los "favoritos/videoteca genérica" de su Media center.'
    txt += ' o bien, añadir el contenido de Preferidos de Balandro a la "Videoteca genérica" de su Media center, con el addon externo "ADD TO LIB"'

    platformtools.dialog_textviewer('Preferidos y su Funcionamiento', txt)


def show_help_tracking_update(item):
    logger.info()

    txt = '[COLOR gold]¿ Qué es el servicio de búsqueda de nuevos episodios ?[/COLOR][CR]'
    txt += 'El servicio es un proceso de Balandro que se ejecuta al iniciarse su Media Center, y se encarga de comprobar cuando hay que buscar actualizaciones.'
    txt += ' En la configuración dentro de "Actualizar" puedes indicar cada cuanto tiempo deben hacerse las comprobaciones.'
    txt += ' Por defecto es dos veces al día, cada 12 horas, pero puedes cambiarlo.'
    txt += ' Si lo tienes desactivado, puedes ejecutar manualmente la misma búsqueda desde el menú contextual de "Series" dentro de "Preferidos".'

    txt += '[CR][CR][COLOR gold]¿ Cómo se activa la búsqueda de nuevos episodios para series ?[/COLOR][CR]'
    txt += 'Desde el listado de series dentro de "Preferidos" accede a "Gestionar serie" desde el menú contextual.'
    txt += ' Al seleccionar "Programar búsqueda automática de nuevos episodios" podrás definir el seguimiento que quieres darle a la serie'
    txt += ' e indicar cada cuanto tiempo hay que hacer la comprobación de si hay nuevos episodios.'

    txt += '[CR][CR][COLOR gold]¿ Cómo se combina el servicio con las series ?[/COLOR][CR]'
    txt += 'Cada vez que se ejecuta el servicio (1, 2, 3 o 4 veces por día) se buscan las series que tienen activada la búsqueda automática.'
    txt += ' Por cada serie según su propia periodicidad se ejecuta o no la búsqueda.'
    txt += ' Esto permite por ejemplo tener series que sólo requieren una actualización por semana, y otras dónde conviene comprobar cada día.'

    txt += '[CR][CR][COLOR gold]¿ Por qué la búsqueda de nuevos episodios está desactivada por defecto ?[/COLOR][CR]'
    txt += 'Es preferible ser prudente con las actualizaciones para no saturar más las webs de dónde se obtiene la información.'
    txt += ' Por esta razón al guardar series por defecto no tienen activada la comprobación de nuevos episodios y hay que indicarlo explícitamente si se quiere.'
    txt += ' Si por ejemplo sigues una serie ya terminada seguramente no necesitarás buscar nuevos episodios, en cambio si sigues una serie de un show diario sí te interesará.'

    txt += '[CR][CR][COLOR gold]¿ Dónde se ven los nuevos episodios encontrados ?[/COLOR][CR]'
    txt += 'En "Preferidos" estarán dentro de sus series respectivas, pero también se puede ver un listado de los últimos episodios añadidos'
    txt += ' por fecha de emisión o de actualización en los canales.'

    platformtools.dialog_textviewer('Búsqueda automática de nuevos episodios', txt)


def show_help_proxies(item):
    logger.info()

    txt = '[COLOR gold]¿ Por qué en algunos canales hay una opción para configurar proxies ?[/COLOR][CR]'
    txt += 'Ciertos canales sufren bloqueos por parte de algunos países/operadoras que no permiten acceder a su contenido.'
    txt += ' Mediante el uso de proxies se puede evitar esa restricción.'

    txt += '[CR][CR][COLOR gold]¿ En qué canales hay que usar los proxies ?[/COLOR][CR]'
    txt += 'Depende de la conexión de cada usuario (el país dónde se conecta, con qué operadora, qué dns tiene configurados, si usa o no vpn, ...).'
    txt += ' Lo más aconsejable es probar primero si funcionan sin necesidad de proxies ya que es lo más cómodo y rápido.'
    txt += ' Aunque un canal tenga la opción de proxies no es obligatorio usarlos, hacerlo solamente si es necesario.'

    txt += '[CR][CR][COLOR gold]¿ Se pueden descartar los canales que requieren proxies ?[/COLOR][CR]'
    txt += 'Sí, desde la opción dentro de buscar [COLOR gold]Excluir canales en las búsquedas[/COLOR].'
    txt += 'También, desde el listado de canales de películas y/o series, en el menú contextual se pueden desactivar los canales deseados.'
    txt += ' De esta manera quedarán descartados para las búsquedas globales, se evitarán sus mensajes relacionados con los proxies'
    txt += ' y se acelerará la búsqueda.'

    txt += '[CR][CR][COLOR gold]¿ Cómo se usa la configuración de proxies ?[/COLOR][CR]'
    txt += 'Por defecto en la configuración de Balandro esta activada la opción "Buscar proxies automaticamente" ello efectua un barrido de búsqueda de acuerdo con el proveedor informado.'
    txt += '[CR][CR]'
    txt += 'En la configuración de "Proxies" se pueden personalizar (Dejar de buscar si se hallaron suficientes válidos, Proveedor de proxies habitual, Limitar la cantidad de válidos a memorizar,'
    txt += ' las solicitudes de Anonimidad, País, etc.)'
    txt += '[CR][CR]'
    txt += 'Una vez finalizado el proceso de búsqueda presentará la consola de resultados con varias opciones.'
    txt += '[CR][CR]'
    txt += 'La 1ra opción (Modificar manualmente) sirve por si se quieren escribir los proxies a usar.'
    txt += ' La 2da opción (Buscar nuevos proxies) sirve para realizar una búsqueda de proxies que pueden servir para el canal. Los tres más rápidos entre los válidos se guardarán en la configuración del canal.'
    txt += ' La 3ra opción (Parámetros para buscar) sirve para configurar ciertas opciones para la búsqueda de proxies. Normalmente las opciones por defecto son suficientes pero si fallan se puede probar cambiando algún parámetro (la web de dónde se obtienen, el tipo de proxy, ...).'

    txt += '[CR][CR][COLOR gold]¿ Se ralentizan los canales si se utilizan proxies ?[/COLOR][CR]'
    txt += 'Sí, acceder a las webs de los canales a través de proxies ralentiza considerablemente lo que tardan en responder.'
    txt += ' Aún así, hay proxies más rápidos que otros, o más estables, o menos saturados, gratuítos o de pago, etc.'

    txt += '[CR][CR][COLOR gold]¿ Por qué muchos proxies dejan de funcionar ?[/COLOR][CR]'
    txt += 'Los proxies que se pueden encontrar en la búsqueda son todos gratuítos pero tienen ciertas limitaciones y no siempre están activos.'
    txt += ' Para cada canal se guardan los proxies a utilizar, pero es posible que algunos días cuando entres tengas que volver a hacer una búsqueda de proxies porque han dejado de funcionar.'

    platformtools.dialog_textviewer('Utilización de proxies', txt)


def show_version(item):
    logger.info()

    try:
       with open(os.path.join(config.get_runtime_path(), 'version.txt'), 'r') as f: txt=f.read(); f.close()

       platformtools.dialog_textviewer('Información versión', txt)
       return True
    except:
       return False

def show_changelog(item):
    logger.info()

    try:
       with open(os.path.join(config.get_runtime_path(), 'changelog.txt'), 'r') as f: txt=f.read(); f.close()

       platformtools.dialog_textviewer('Historial de cambios', txt)
    except:
       pass

def show_dev_notes(item):
    logger.info()

    try:
       with open(os.path.join(config.get_runtime_path(), 'dev-notes.txt'), 'r') as f: txt=f.read(); f.close()

       platformtools.dialog_textviewer('Notas para developers', txt)
    except:
       pass


def show_log(item):
    logger.info()

    loglevel = config.get_setting('debug', 0)
    if not loglevel >= 2:
        if not platformtools.dialog_yesno(config.__addon_name, 'El nivel actual de información del fichero LOG de su Media Center NO esta configurado al máximo. ¿ Desea no obstante visualizarlo ?'): 
            return

    path = translatePath(os.path.join('special://logpath/', ''))

    file_log = 'kodi.log'

    file = path + file_log

    existe = filetools.exists(file)

    if existe == False:
        files = filetools.listdir(path)
        for file_log in files:
            if file_log.endswith('.log') == True:
                file = path + file_log
                existe = filetools.exists(file)
                break

    if existe == False:
        platformtools.dialog_notification(config.__addon_name, 'No se localiza su fichero Log')
        return

    size = filetools.getsize(file)
    if size > 999999:
        platformtools.dialog_notification(config.__addon_name, 'Cargando fichero log')

    try:
       with open(os.path.join(path, file_log), 'r') as f: txt=f.read(); f.close()

       platformtools.dialog_textviewer('Fichero LOG de su Media Center', txt)
    except:
       pass


def copy_log(item):
    logger.info()

    loglevel = config.get_setting('debug', 0)
    if not loglevel >= 2:
        if not platformtools.dialog_yesno(config.__addon_name, 'El nivel actual de información del fichero LOG de su Media Center NO esta configurado al máximo. ¿ Desea no obstante obtener una copia ?'): 
            return

    path = translatePath(os.path.join('special://logpath/', ''))

    file_log = 'kodi.log'

    file = path + file_log

    existe = filetools.exists(file)

    if existe == False:
        files = filetools.listdir(path)
        for file_log in files:
            if file_log.endswith('.log') == True:
                file = path + file_log
                existe = filetools.exists(file)
                break

    if existe == False:
        platformtools.dialog_notification(config.__addon_name, 'No se localiza su fichero Log')
        return

    import xbmcgui
    destino_path = xbmcgui.Dialog().browseSingle(3, 'Seleccionar carpeta dónde copiar', 'files', '', False, False, '')
    if not destino_path: return False

    origen = os.path.join(path, file_log)
    destino = filetools.join(destino_path, file_log)
    if not filetools.copy(origen, destino, silent=False):
        platformtools.dialog_ok(config.__addon_name, 'Error, no se ha podido copiar el fichero Log!', origen, destino)
        return False

    platformtools.dialog_notification('Fichero Log copiado', file_log)


def show_advs(item):
    logger.info()

    path = translatePath(os.path.join('special://home/userdata', ''))

    file_advs = 'advancedsettings.xml'

    file = path + file_advs

    existe = filetools.exists(file)

    if existe == False:
        platformtools.dialog_notification(config.__addon_name, 'No hay fichero Advancedsettings')
        return

    try:
       with open(os.path.join(path, file_advs), 'r') as f: txt=f.read(); f.close()

       platformtools.dialog_textviewer('Su fichero Advancedsettings de su Media Center', txt)
    except:
        pass


def show_help_adults(item):
    logger.info()

    txt = '*) Las webs podrian, en algún caso, publicar Vídeos con contenido [COLOR gold]No Apto[/COLOR] para menores.'
    txt += ' Balandro cuenta con un apartado en su configuración exclusivo para el [COLOR gold]Control Parental[/COLOR].'
    txt += ' (por defecto este apartado está [COLOR gold]Habilitado[/COLOR]).'

    txt += '[CR][CR]'
    txt += '*) Pero no se puede garantizar que todo el material de este tipo se filtre correctamente en determinadas ocasiones.'

    platformtools.dialog_textviewer('Control Parental', txt)


def show_help_torrents(item):
    logger.info()

    txt = '*) A través de un navegador web localize e instale al menos uno de los add-ons de la lista que más se adapte a'
    txt += '  sus necesidades y que sea a su vez compatible con su Media Center.'

    txt += '[CR][CR]'
    txt += '*) Add-Ons:[CR]'
    txt += '    - plugin.video.quasar[CR]'
    txt += '    - plugin.video.elementum[CR]'
    txt += '    - plugin.video.torrenter[CR]'
    txt += '    - plugin.video.torrentin[CR]'
    txt += '    - plugin.video.torrest[CR]'
    txt += '    - plugin.video.pulsar[CR]'
    txt += '    - plugin.video.stream[CR]'
    txt += '    - plugin.video.xbmctorrent'

    txt += '[CR][CR]'
    txt += '*) A modo de ejemplo para [COLOR gold]Elementum[/COLOR] puede acceder a su web oficial en "elementum.surge.sh"'

    txt += '[CR][CR]'
    txt += '*) Existen múltiples sitios webs en donde puede localizar estos add-ons, entre estos sitios le recomendamos'
    txt += '   acceda a este [COLOR gold]fuentekodileia.github.io[/COLOR]'

    platformtools.dialog_textviewer('¿ Dónde obtener los add-ons para torrents ?', txt)


def show_legalidad(item):
    logger.info()

    txt = '*)[COLOR yellow][B] Balandro [COLOR moccasin][B] Es Totalmente [I] GRATUITO [/I], si Pagó Por Este Add-On le [I] ENGAÑARON [/I][/B][/COLOR]'
    txt += '[COLOR lightblue][B] y Tiene Como Objeto, Permitir Visualizar Películas, Series y Documentales, etc... [/B][/COLOR]'
    txt += '[COLOR lightblue][B] Todo a Través de Internet y Directamente Desde su Sistema Media Center. [/B][/COLOR]'

    txt += '[CR][CR][COLOR orchid][B] Este Add-On es Tan Solo un Mero Ejercicio de Aprendizaje Del Lenguaje de Programación Python y se Distribuye Sin Ningún Contenido Multimedia Adjunto al Mismo [/B][/COLOR]'
    txt += '[COLOR lightgrey][B][I] En Consecuencia Solo Las Webs Son Plenamente Responsables de Los Contenidos Que Publiquen [/I][/B][/COLOR]'

    txt += '[CR][CR][COLOR tan][B] Úselo de Acuerdo Con su Criterio y Bajo su Responsabilidad [/B][/COLOR]'
    txt += '[COLOR tan][B] Sus  Creadores Quedarán Totalmente Eximidos de Toda Repercusión Legal, si se Re-Distribuye Solo o Con Acceso a Contenidos Protegidos Por Los Derechos de Autor, Sin el Permiso Explicito de Los Mismos[/B][/COLOR]'

    txt += '[CR][CR]*)[COLOR chocolate][B][I] Si Este Tipo de Contenido Está Prohibido en su País, Solamente Usted Será el Responsable de su Uso [/I][/B][/COLOR] '

    txt += '[CR][CR]*)[COLOR mediumaquamarine][B] Este Add-On es un Proyecto Sin Ánimo de Lucro y Con Fines Educativos, Por lo Tanto Está Prohibida su Venta en Solitario o Como Parte de Software Integrado en Cualquier Dispositivo, es Exclusivamente Para un Uso Docente y Personal [/B][/COLOR] '

    txt += '[CR][CR]*)[COLOR red][B][I] Queda Totalmente Prohibida su Re-Distribución, Sin la Autorización Fehaciente de Sus Creadores [/I][/B][/COLOR] '

    platformtools.dialog_textviewer('Cuestiones Legales', txt)


def show_license(item):
    logger.info()

    try:
       with open(os.path.join(config.get_runtime_path(), 'LICENSE'), 'r') as f: txt=f.read(); f.close()

       platformtools.dialog_textviewer('Licencia (Gnu Gpl v3)', txt)
    except:
       pass


def show_test(item):
    import xbmc, platform

    from core import httptools, channeltools, scrapertools

    platformtools.dialog_notification(config.__addon_name, 'Cargando información sistema')

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

    hay_repo = False
    if xbmc.getCondVisibility('System.HasAddon("%s")' % 'repository.balandro'): hay_repo = True

    access_repo = False
    tex_access_repo = ''
    if hay_repo:
        ADDON_REPO_ADDONS = 'https://balandro.tk/repo/addons.xml'
        try:
           data = httptools.downloadpage(ADDON_REPO_ADDONS).data
           if data: access_repo = True
        except:
           tex_access_repo = '[COLOR blue]No se ha podido comprobar[/COLOR]'

    last_ver = ''
    access_last_ver = False
    if hay_repo:
        if access_repo:
            last_ver = scrapertools.find_single_match(data, 'name="' + config.__addon_name + '.*?version="(.*?)"')
            if last_ver: access_last_ver = True

    access_fixes = False
    tex_access_fixes = ''
    if hay_repo:
        if access_repo:
            ADDON_UPDATES_JSON = 'https://balandro.tk/addon_updates/updates.json'
            try:
               data = httptools.downloadpage(ADDON_UPDATES_JSON).data
               if data:
                   access_fixes = True
                   if 'addon_version' not in data or 'fix_version' not in data:
                       access_fixes = None
            except:
               tex_access_fixes = '[COLOR blue]No se ha podido comprobar[/COLOR]'


    txt = '[CR][CR][COLOR fuchsia]Balandro[/COLOR][CR]'

    if not hay_internet: 
        if your_ip == '': your_ip = '[COLOR red] Sin Conexión [/COLOR]'

    txt += '- [COLOR gold]Conexión internet:[/COLOR]  %s ' % your_ip
    txt += '[CR][CR]'

    tex_repo = ' Instalado'
    if hay_repo == False: tex_repo = '[COLOR red] No está instalado, No recibirás más versiones [/COLOR]'


    txt += '- [COLOR gold]Repositorio:[/COLOR]  %s ' % tex_repo
    txt += '[CR][CR]'
    tex_access_repo = ' Accesible'
    if access_repo == False:
        if tex_access_repo == '':
            tex_access_repo = '[COLOR red] Sin conexión No accesible [/COLOR]'

    txt += '- [COLOR gold]Conexión con repositorio:[/COLOR]  %s ' % tex_access_repo
    txt += '[CR][CR]'

    if access_last_ver:
        tex_access_last_ver = '  ' + last_ver
    else: tex_access_last_ver = '[COLOR red] Última versión No accesible [/COLOR]'

    txt += '- [COLOR gold]Última versión:[/COLOR]  %s ' % tex_access_last_ver
    txt += '[CR][CR]'

    if not tex_access_fixes:
        tex_access_fixes = ' Accesibles'
        if access_fixes == None: tex_access_fixes = '[COLOR yellow] No hay actualizaciones tipo Fix pendientes [/COLOR]'
        elif access_fixes == False: tex_access_fixes = '[COLOR red] Fixes sobre ´última versión No accesibles [/COLOR]'

    txt += '- [COLOR gold]Fixes sobre última versión:[/COLOR]  %s ' % tex_access_fixes
    txt += '[CR][CR]'

    txt += '- [COLOR gold]Versión instalada:[/COLOR]  [COLOR yellow][B]%s[/B][/COLOR]' % config.get_addon_version()
    txt += '[CR][CR]'

    folder_down = config.get_setting('downloadpath', default='')
    if not folder_down == '':
        txt += '- [COLOR gold]Carpeta descargas:[/COLOR]  [COLOR moccasin]%s[/COLOR]' % folder_down
        txt += '[CR][CR]'


    tex_dom = ''
    cinecalidad_dominio = config.get_setting('channel_cinecalidad_dominio', default='')
    if not cinecalidad_dominio == '': tex_dom = tex_dom + cinecalidad_dominio + '  '

    hdfull_dominio = config.get_setting('channel_hdfull_dominio', default='')
    if not hdfull_dominio == '': tex_dom = tex_dom + hdfull_dominio

    if tex_dom:
        txt += '- [COLOR gold]Dominios:[/COLOR]  [COLOR springgreen]%s[/COLOR]' %  str(tex_dom)
        txt += '[CR][CR]'

    filtros = {'searchable': True}
    opciones = []

    ch_list = channeltools.get_channels_list(filtros=filtros)

    if ch_list:
       txt_ch = ''

       for ch in ch_list:
           cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'
           cfg_proxytools_max_channel = 'channel_' + ch['id'] + '_proxytools_max'

           if not config.get_setting(cfg_proxies_channel, default=''):
               if not config.get_setting(cfg_proxytools_max_channel, default=''):
                   continue

           txt_ch += '[COLOR red]%s[/COLOR]  ' % ch['name']

       if not txt_ch: txt_ch = 'No hay canales con proxies' 
       txt += '- [COLOR gold]Proxies:[/COLOR]  %s' %  str(txt_ch)

    cliente_torrent = config.get_setting('cliente_torrent', default='Ninguno')
    if cliente_torrent == 'Ninguno': tex_tor = '[COLOR moccasin]Ninguno[/COLOR]'
    elif cliente_torrent == 'Seleccionar':  tex_tor = 'Seleccionar'
    else:
      tex_tor = cliente_torrent
      cliente_torrent = 'plugin.video.' + cliente_torrent.lower()
      if xbmc.getCondVisibility('System.HasAddon("%s")' % cliente_torrent):
          tex_tor += '  Instalado'
      else:
          tex_tor += '  [COLOR red]No instalado[/COLOR]'

    txt += '[CR][CR]- [COLOR gold]Motor torrent:[/COLOR]  %s' % tex_tor

    loglevel = config.get_setting('debug', 0)
    if loglevel == 0: tex_niv = 'Solo Errores'
    elif loglevel == 1: tex_niv = 'Errores e Información'
    else: tex_niv = 'Máxima Información'

    txt += '[CR][CR]- [COLOR gold]Log:[/COLOR]  %s' % tex_niv

    txt += '[CR][CR][COLOR fuchsia]Entorno[/COLOR][CR]'

    txt += '- [COLOR gold]Media center:[/COLOR]  [COLOR coral]%s[/COLOR]' % str(xbmc.getInfoLabel('System.BuildVersion'))
    txt += '[CR][CR]'

    plataforma = platform.uname()

    txt += '- [COLOR gold]Sistema:[/COLOR]  %s-%s-%s' %  (str(plataforma[0]), str(plataforma[2]), str(plataforma[3]))
    txt += '[CR][CR]'

    txt += '- [COLOR gold]Python:[/COLOR]  %s.%s.%s' % (str(sys.version_info[0]), str(sys.version_info[1]), str(sys.version_info[2]))
    txt += '[CR][CR]'

    if last_ver:
        if not config.get_addon_version() == last_ver:
            platformtools.dialog_ok(config.__addon_name, 'Versión instalada[COLOR coral][B] ' + config.get_addon_version() + '[/B][/COLOR]', 'Última Versión disponible [COLOR yellow][B] ' + last_ver + '[/B][/COLOR]')

    platformtools.dialog_textviewer('Test status sistema', txt)


def show_last_fix(item):
    logger.info()

    path = os.path.join(config.get_runtime_path(), 'last_fix.json')

    existe = filetools.exists(path)
    if existe == False:
        platformtools.dialog_notification(config.__addon_name, 'No hay fichero Fix')
        return

    try:
       with open(path, 'r') as f: txt=f.read(); f.close()

       txt = txt.replace('{', '').replace('}', '').replace('[', '').replace(']', '').replace(',', '').replace('"', '').replace("'", '').strip()

       platformtools.dialog_textviewer('Información del último Fix instalado', txt)
    except:
       pass


def show_sets(item):
    logger.info()

    file_sets = os.path.join(config.get_data_path(), "settings.xml")

    existe = filetools.exists(file_sets)

    if existe == False:
        platformtools.dialog_notification(config.__addon_name, '[COLOR red]No existe settings.xml[/COLOR]')
        return

    try:
       with open(os.path.join(file_sets), 'r') as f: txt=f.read(); f.close()

       platformtools.dialog_textviewer('Su fichero de Ajustes personalizados', txt)
    except:
       pass


def show_cook(item):
    logger.info()

    file_cook = os.path.join(config.get_data_path(), "cookies.dat")

    existe = filetools.exists(file_cook)

    if existe == False:
        platformtools.dialog_notification(config.__addon_name, '[COLOR red]No existe cookies.dat[/COLOR]')
        return

    try:
       with open(os.path.join(file_cook), 'r') as f: txt=f.read(); f.close()

       platformtools.dialog_textviewer('Su fichero de Cookies', txt)
    except:
       pass
