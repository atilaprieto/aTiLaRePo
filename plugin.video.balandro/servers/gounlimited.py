# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger
from lib import jsunpack


def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)

    vid = scrapertools.find_single_match(page_url, "gounlimited.to/(?:embed-|)([A-z0-9]+)")
    if not vid: vid = scrapertools.find_single_match(page_url, "tazmovies.com/(?:embed-|)([A-z0-9]+)")

    video_urls = get_embed(vid)
    if len(video_urls) == 0:
        video_urls = get_download(vid)

    return video_urls


def get_embed(vid):
    video_urls = []

    data = httptools.downloadpage('https://gounlimited.to/embed-' + vid + '.html').data
    # ~ logger.debug(data)

    packer = scrapertools.find_single_match(data, "<script type='text/javascript'>(eval.function.p,a,c,k,e,d..*?)</script>")
    if packer:
        data = jsunpack.unpack(packer)
        # ~ logger.debug(data)

    mp4 = scrapertools.find_single_match(data, 'sources:\["([^"]+)')
    if not mp4: mp4 = scrapertools.find_single_match(data, 'src:"([^"]+\.mp4)"')
    if mp4 and descartable(mp4): return 'Servidor sobrecargado, no se puede reproducir'
    if mp4: 
        subtitulos = scrapertools.find_single_match(data, 'src:"([^"]+\.vtt)"')
        video_urls.append(["mp4", mp4, 0, subtitulos])

    return video_urls


def get_download(vid):
    video_urls = []

    data = httptools.downloadpage('https://gounlimited.to/' + vid).data
    # ~ logger.debug(data)

    matches = scrapertools.find_multiple_matches(data, "download_video\('([^']+)','([^']+)','([^']+)'")
    for p0, p1, p2 in matches:
        url = 'https://gounlimited.to/dl?op=download_orig&id=%s&mode=%s&hash=%s' % (p0, p1, p2)
        data = httptools.downloadpage(url).data
        # ~ logger.debug(data)
        
        url = scrapertools.find_single_match(data, ' href="([^"]+)">Direct Download Link</a>')
        if url and not descartable(url):
            video_urls.append(["mp4", url])

    return video_urls

# Descartar vídeos fake de "This server is extremely overloaded, unfortunately ..."
def descartable(url):
    # ~ https://gounlimited.to/videojs7/small3.mp4
    # ~ https://xxx.gounlimited.to/xxx/SampleVideo_720x480_2mb.mp4
    if 'small3.mp4' in url or 'SampleVideo_' in url: return True
    else: return False
