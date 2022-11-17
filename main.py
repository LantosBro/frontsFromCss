import cssutils
import getopt
import sys
import re
import requests
from urllib.parse import urlparse, unquote
from pathlib import Path
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool


def download_url(args):
    url, fn = args[0], args[1]
    try:
        r = requests.get(url)
        with open(fn, 'wb') as f:
            f.write(r.content)
        return url
    except Exception as e:
        print('Exception in download_url():', e)


def download(args):
    cpus = cpu_count()
    results = ThreadPool(cpus - 1).imap_unordered(download_url, args)
    for result in results:
        print('url:', result)

def main(argv):
    input = ''

    try:
        opts, args = getopt.getopt(argv, "hi:", ["input="])
    except getopt.GetoptError:
        print('frontsFromCss.py -i <input>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('frontsFromCss.py -i <input>')
            sys.exit()
        elif opt in ("-i", "--input"):
            input = arg

    css_arr = []
    url_arr = []
    filename_arr = []
    sheet = cssutils.parseFile(input)

    for rule in sheet:
        if rule.type == rule.FONT_FACE_RULE:
            for property in rule.style:
                if property.name == 'src':
                    css_arr.append(property.value.split(','))

    for rawUrls in css_arr:
        for rawUrl in rawUrls:
            url_arr.append(re.search(
                r'\b(?:https?|telnet|gopher|file|wais|ftp):[\w/#~:.?+=&%@!\-.:?\\-]+?(?=[.:?\-]*(?:[^\w/#~:.?+=&%@!\-.:?\-]|$))',
                rawUrl).group(0))

    for url in url_arr:
        url_parsed = urlparse(url)
        filename_arr.append(str(Path("./") / unquote(Path(url_parsed.path).name)))

    urls_and_names = zip(url_arr, filename_arr)

    download(urls_and_names)


if __name__ == "__main__":
    main(sys.argv[1:])
