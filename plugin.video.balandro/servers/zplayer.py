# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger
from lib import jsunpack


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    if "File is no longer available" in data:
        return 'El fichero no existe o ha sido borrado'

    if not 'v2.zplayer' in page_url:
        matches = scrapertools.find_multiple_matches(data, '"file": "([^"]+)",.*?"type": "([^"]+)"')

        for video_url, ext in matches:
            ref = scrapertools.find_single_match(video_url, '(.*?&)') + "shared=%s" % page_url
            headers = {"Referer":page_url}

            if "redirect"  in video_url: 
                url = httptools.downloadpage(video_url, headers=headers, follow_redirects=False, only_headers=True).headers.get("location", "")
                if not url: continue

                url += "|Referer=%s" % page_url
            else:
                url = video_url + "|Referer=%s" % ref

            video_urls.append([ext, url])
    else:
        packed = scrapertools.find_single_match(data, "text/javascript'>(eval.*?)\s*</script>")
        unpacked = jsunpack.unpack(packed)
        matches = scrapertools.find_multiple_matches(unpacked, r'sources:\[\{\s*file:"([^"]+)"')

        for video_url in matches:
            ext = video_url[-4:]
            video_url += "|Referer=https://v2.zplayer.live/"

            video_urls.append([ext, url])

    return video_urls
