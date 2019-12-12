# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para azteca 13 y azteca 7
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

from core import scrapertools
from core import logger

from lib import youtube_dl

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("tvalacarta.servers.azteca get_video_url page_url="+page_url)

    data = scrapertools.cache_page(page_url)
    page_url = scrapertools.find_single_match(data,'<meta property="og:video" content="([^"]+)"/>')
    logger.info("tvalacarta.servers.azteca get_video_url page_url="+page_url)

    ydl = youtube_dl.YoutubeDL({'outtmpl': u'%(id)s%(ext)s'})
    result = ydl.extract_info(page_url, download=False)
    video_urls = []
    if 'formats' in result:
        for entry in result['formats']:
            logger.info("entry="+repr(entry))

            '''
            {u'http_headers': 
                {
                u'Accept-Charset': u'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 
                u'Accept-Language': u'en-us,en;q=0.5', 
                u'Accept-Encoding': u'gzip, deflate', 
                u'Accept': u'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
                u'User-Agent': u'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20150101 Firefox/44.0 (Chrome)'}, 
                u'protocol': u'm3u8_native', 
                u'format': u'hls-582 - 640x360', 
                u'url': u'http://tvazvod-i.akamaihd.net/i/p/459791/sp/45979100/serveFlavor/entryId/0_pcso1cnx/v/2/flavorId/0_qx9uhlyx/index_0_av.m3u8', 
                u'tbr': 582, 
                u'height': 360, 
                u'width': 640, 
                u'ext': u'mp4', 
                u'preference': None, 
                u'format_id': u'hls-582'
            }
            '''
            video_urls.append([scrapertools.safe_unicode(entry['format']).encode('utf-8'), scrapertools.safe_unicode(entry['url']).encode('utf-8')])
            #logger.info('Append: {}'.format(entry['url']))

    video_urls.reverse()

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve
