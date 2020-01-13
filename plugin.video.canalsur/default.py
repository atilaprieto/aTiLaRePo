import sys
import xbmcgui
import xbmcplugin
import xbmc
import urllib
import urllib2
import urlparse
import xbmcaddon
import os
import re
import unicodedata
import plugintools
from HTMLParser import HTMLParser
from types import UnicodeType
 
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
my_addon = xbmcaddon.Addon()
PATH = my_addon.getAddonInfo('path')
sys.path.append(xbmc.translatePath(os.path.join(PATH, 'lib')))

channellist = [
    [
        "YouTube - Canal Sur",
        "user/canalsur",
        "https://yt3.ggpht.com/a/AGF-l79qnYhlfv7OSNOJuIT0Afs56eXq23cAbrDjcA=s288-c-k-c0xffffffff-no-rj-mo"
    ],[
        "YouTube - Al Sur",
        "channel/UC6p2vL5o7jhHS1fgjQa1hNQ",
        "https://yt3.ggpht.com/a/AGF-l794Ct-RHmzl1CxvViXCN9aPFGkqHTz_BfttUw=s288-c-k-c0xffffffff-no-rj-mo"
    ],[
        "YouTube - Canal Andalucia Cocina",
        "channel/UCfvJGXiVIj6OzCutOpcDPPQ",
        "https://yt3.ggpht.com/a/AGF-l7_1bNL27WctItXYSZez3Eb8ng2dIP9qsaJUWA=s288-c-k-c0xffffffff-no-rj-mo"
    ],[
        "YouTube - Canal Andalucia Flamenco",
        "channel/UCWyKqd2is0VtWn2qKexkYpw",
        "https://yt3.ggpht.com/a/AGF-l7-FHUfiv7lasGhCVf4Q_BeDvF72PeRFr0GIIA=s288-c-k-c0xffffffff-no-rj-mo"
    ],[
        "YouTube - Canal Sur Andalucia Directo",
        "user/canalsurad",
        "https://yt3.ggpht.com/a/AGF-l7_Wc_lsoR5ywK14Z0biMQRN4w98Vwb-K-lHEg=s288-c-k-c0xffffffff-no-rj-mo"
    ],[
        "YouTube - Canal Sur Turismo",
        "channel/UC9iTd-w6-4OVnWrIZjw4akQ",
        "https://yt3.ggpht.com/a/AGF-l7_2A9dek75hCStsPqzUncg7JSVB3UiY8y5-ag=s288-c-k-c0xffffffff-no-rj-mo"
    ],[
        "YouTube - CarnavalSur",
        "channel/UCQcjDEVrrnRCgx99035ADtw",
        "https://yt3.ggpht.com/a/AGF-l780pqcZZGo4lFFHn6Z9euy1-QPwqLmZ7W0YRg=s288-c-k-c0xffffffff-no-rj-mo"
    ],[
        "YouTube - EducAccion.tv",
        "user/educacciontv",
        "https://yt3.ggpht.com/a/AGF-l7-ctm-P7KRog7wSI1wPN2HG3Y0CEsZwJh2FEA=s288-c-k-c0xffffffff-no-rj-mo"
    ],[
        "YouTube - ElDebate 5C",
        "channel/UCKluhFEobeDFAEKIiN-eHvw",
        "https://yt3.ggpht.com/a/AGF-l7_M2FU2p-72CsGf3O_A6FlGom6RD8wR_9JhFA=s288-c-k-c0xffffffff-no-rj-mo"
    ],[
        "YouTube - El Tiempo Canal Sur",
        "user/EltiempoCanalSur",
        "https://yt3.ggpht.com/a/AGF-l7-19if4hSAbGCCdTBiSr6YAsXiQ9R71RlsrDw=s288-c-k-c0xffffffff-no-rj-mo"
    ],[
        "YouTube - Filmoteca de Andalucia",
        "user/filmotecadeandalucia",
        "https://yt3.ggpht.com/a/AGF-l7-C2ylv04oc_r_rcUkau59U7nuoozkh0GZFeA=s288-c-k-c0xffffffff-no-rj-mo"
    ],[
        "YouTube - La Tarde Aqui y Ahora",
        "user/latardeaquiyahora",
        "https://yt3.ggpht.com/a/AGF-l7-bPF4VzRzE0lzIZhq88yJhpYbFNyff5an8=s288-c-k-c0xffffffff-no-rj-mo"
    ],[
        "YouTube - losreporterosCSTV",
        "channel/UCCYmeVKhticSKG2VjzqasWw",
        "https://yt3.ggpht.com/a/AGF-l78kmrIfOPV5DAbpen66ugqdJ73ER2_VVSZwuw=s288-c-k-c0xffffffff-no-rj-mo"
    ],[
        "YouTube - MemorANDA",
        "channel/UC_dkgVvhcZlxqceYSCC-MNw",
        "https://yt3.ggpht.com/a/AGF-l7_j3MCWppcH9fzU8W1DBc9Dgyi6LBLNMCFlIA=s288-c-k-c0xffffffff-no-rj-mo"
    ],[
        "YouTube - Solidarios CanalSur",
        "channel/UC-6dzPuzF-WZA4KWQjg1z9Q",
        "https://yt3.ggpht.com/a/AGF-l78VWJ8nQgbYEsVSr4qyCiNdGiIIQJn24arXNg=s288-c-k-c0xffffffff-no-rj-mo"
    ],[
        "YouTube - Testigos Hoy",
        "user/testigoshoy",
        "https://yt3.ggpht.com/a/AGF-l7-rzVv8LdSsUxS9xOIQNuOoZQv4wDEy4Tl1Lw=s288-c-k-c0xffffffff-no-rj-mo"
    ],[
        "YouTube - Tierra de Talento",
        "channel/UCsE-BcBHMRRGzGrFAgOhp1Q",
        "https://yt3.ggpht.com/a/AGF-l7_EHNygo50jYw1_pMFw3SrQk0OHO-D46EqSZQ=s288-c-k-c0xffffffff-no-rj-mo"
    ],[
        "YouTube - Tierra y Mar & Espacio Protegido Canal Sur",
        "channel/UC-njJWxX7B_Onpld-Z9aDOA",
        "https://yt3.ggpht.com/a/AGF-l7-v1mzOIgN6Fi93uWBUocmc6kGFYWPHuPbObg=s288-c-k-c0xffffffff-no-rj-mo"
    ],[
        "YouTube - Toros para todos Canal Sur",
        "channel/UClGdlNjS57b73yEpIis-eVA",
        "https://yt3.ggpht.com/a/AGF-l79kQ4vuZHEbUnkUf-Igu3gwcljKJzNq1eFPpQ=s288-c-k-c0xffffffff-no-rj-mo"
    ]
]

def strip_accents(text):
    try:
        text = unicode(text.encode("utf-8"), 'utf-8')
    except NameError:
        pass
    text = unicodedata.normalize('NFD', text)\
           .encode('ascii', 'ignore')\
           .decode("utf-8")
    return str(text)

def only_legal_chars(string_in):
    string_out = re.sub(r'[#\\/:"*?<>|]+', "", string_in)
    string_out = "".join(i for i in string_out if ord(i)<128)
    string_out = ' '.join(string_out.split())
    return string_out

def utf8me(string_in):
    return safe_unicode(string_in).encode('utf-8')

def safe_unicode(value):
    if type(value) is UnicodeType:
        return value
    else:
        try:
            return unicode(value, 'utf-8')
        except:
            return unicode(value, 'iso-8859-1')
 
def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

def decode_html(value):
    try:
        unicode_title = unicode(value, "utf8", "ignore")
        return utf8me(HTMLParser().unescape(unicode_title).encode("utf8"))
    except:
        return utf8me(value)

def browse_this_shit(url_in):
    try:
        request = urllib2.Request(url_in)
        return urllib2.urlopen(request).read()
    except:
        return browse_this_shit(url_in)

mode = args.get('mode', None)

if mode is None:

    sections = []

    y = 0
    while True:
        y = y + 1
        index_html = browse_this_shit('http://www.canalsur.es/programas_tv.html?pagina=' + str(y))
        a = index_html.split('<li class="col-xs-12 col-sm-4 col-md-4">')
        if len(a) < 2:
            break
        else:
            for x in range(1, len(a)):
                b = a[x].split('<a href="')
                c = b[1].split('"')
                d = a[x].split("<img src='")
                e = d[1].split("'")
                if '.svg' in e[0]:
                    j = e[0].split('/')
                    k = j[-1].split('.')
                    e[0] = PATH + '/imgs/' + k[0] + '.jpg'
                f = a[x].split('class="nombre_programa">')
                g = f[1].split('</a')
                h = a[x].split('item_description">')
                i = h[1].split('</div')

                sections.append({
                    'legal': only_legal_chars(decode_html(g[0])),
                    'titulo': decode_html(g[0]),
                    'img': e[0],
                    'url': c[0],
                    'texto': decode_html(i[0])
                })
    
    sections = sorted(sections, key = lambda i: i['legal'],reverse=False)

    for item in sections:
        url = build_url({'mode': 'indice', 'title': item['titulo'], 'href': item['url']})
        li = xbmcgui.ListItem(item['titulo'], iconImage = item['img'])
        li.setInfo(type="Video", infoLabels={"plot": item['texto']})
        li.setArt({'fanart': item['img']})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    for name, id, icon in channellist:
        plugintools.add_item(title=name,url="plugin://plugin.video.youtube/"+id+"/",thumbnail=icon,folder=True)

    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'indice':

    show_html = browse_this_shit(urllib.quote(args['href'][0], safe='://-_'))
    a = show_html.split('<div style="margin:0 10px; width:150px; overflow: hidden;" onclick="')

    if len(a) > 1:
        for x in range(1, len(a)):
            b = a[x].split('<img src="')
            c = b[1].split('"')
            d = a[x].split('<span class="titulo">')
            e = d[1].split('</span')
            f = a[x].split('<div class="fecha" ><b><small>')
            g = f[1].split('</small')
            h = a[x].split('overflow: hidden;">')
            i = h[1].split('</div>')
            j = a[x].split('<div class="video" style="display:none;">')
            k = j[1].split('</div>')
            l = k[0].split('::')

            for m in range(0, len(l)):
                li = xbmcgui.ListItem('[B]' + e[0] + '[/B]' + ' - ' + g[0], iconImage=c[0])
                li.setInfo(type="Video", infoLabels={ "plot": i[0], "Title" : '[B]' + e[0] + '[/B]' + ' - ' + g[0]})
                li.setArt({ 'poster': c[0], 'fanart': c[0] })
                li.setProperty("IsPlayable","true")
                xbmcplugin.addDirectoryItem(handle=addon_handle, url=l[m], listitem=li, isFolder=False)
    else:
        a = show_html.split('class="tituloNoticia"')

        urls = []

        for x in range(1, len(a)-1):
            b = a[x].split('href="')
            c = b[-1].split('"')
            if c[0] not in urls:
                urls.append(c[0])

        for x in range(0, len(urls)):

            video_html = browse_this_shit(urls[x])

            b = video_html.split('image:"')
            c = b[1].split('"')
            c[0] = 'http://www.canalsur.es' + c[0]
            d = video_html.split('<title>')
            e = d[1].split('</title>')
            f = video_html.split('<br class="hidden-md hidden-lg"/>')
            
            if len(f) > 1:
                g = f[1].split('</')
                g[0] = ' - ' + g[0].strip()
            else:
                g[0] = ''

            h = video_html.split('<meta name="description" content="')
            i = h[1].split('"/>')
            j = video_html.split('file: "')
            k = j[1].split('"')
            l = k[0].split('::')

            for m in range(0, len(l)):
                li = xbmcgui.ListItem('[B]' + decode_html(e[0]) + '[/B]' + decode_html(g[0]), iconImage=c[0])
                li.setInfo(type="Video", infoLabels={ "plot": decode_html(i[0]), "Title" : '[B]' + decode_html(e[0]) + '[/B]' + decode_html(g[0])})
                li.setArt({ 'poster': c[0], 'fanart': c[0] })
                li.setProperty("IsPlayable","true")
                xbmcplugin.addDirectoryItem(handle=addon_handle, url=l[m], listitem=li, isFolder=False)

    xbmcplugin.endOfDirectory(addon_handle)