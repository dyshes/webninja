from requests_html import HTMLSession
import requests
import reader
import documenter
from profiler import get_keys
import shutil # to save it locally
import re
import os
import json
from time import sleep
import urllib.parse
from reader import view_extractor as read


def get_page(url, render=False):
    if render:
        path="/Applications/Firefox.app/Contents/MacOS/firefox"
        session = HTMLSession()
        req = session.get(url)
        req.html.render(executablePath=path)
        session.close()
    else:
        req = requests.get(url)
    if req.status_code == 200:
        return req.text
    else:
        print(f"Error status: {req.status_code}")
        return "<html></html>"


def get_domain(url):
    try:
        parsed = urllib.parse.urlparse(url)
    except:
        return ""
    return f"{parsed.scheme}://{parsed.netloc}"


def get_image(url, image_name):
    if not get_domain(url):
        print("Invalid URL:", url)
        return
    request = requests.get(url, stream=True)
    if request.status_code == 200:
        request.raw.decode_content = True
        with open(image_name, 'wb') as file:
            shutil.copyfileobj(request.raw, file)
        print('Image Successfully Downloaded:', image_name)
    else:
        print('Image Couldn\'t be retrieved:', url)


def pager(url, reader, max_pages=5):
    """
    Parses website with pages
    :param num: file id
    :param url: initial search url
    :param reader: from html returns next page link
    :param max_pages: max pages to visit
    """
    html = get_page(url)
    visited = []
    while True:
        nl, cp, meta, file = reader(html)
        if not nl:
            print('no next')
            break
        elif int(cp) >= max_pages:
            print('hit max')
            break
        elif cp in visited:
            print('already visited')
            break
        visited.append(cp)
        print('Getting Next Page...')
        sleep(1)
        url = get_domain(url) + nl
        html = get_page(url, render=True)
    return meta, file


def viewer(infile, url, pfilt, vloc, outfile):
    """
    Parses website with no pages
    :param infile: file with profiles
    :param url: target website url
    :param pfilter: returns bool from profile
    :param reader: returns dict from html
    """
    profiles = documenter.read_json(infile)
    print(f'There are {len(profiles)} profiles')
    filts = [pf for pf in profiles if pfilt(pf)]
    print(f'After filter, {len(filts)} profiles')
    for i, pf in enumerate(filts):
        linked = {}
        for key in get_keys(r"link", pf):
            pf[key] = url + pf[key]
            html = get_page(pf[key])
            view = read(html, vloc)
            linked = {**pf, **view}
        print(f"[{i}] has {len(linked)} keys")
        documenter.append_json(linked, outfile)
    return outfile


def image_downloader(file, get_image_name):
    profiles = documenter.read_json(file)
    print('Visiting Images...')
    for profile in profiles:
        for key in get_keys(r"image", profile):
            img = get_image_name(profile[key])
            # download image if it does not exist
            if not os.path.exists(img):
                get_image(profile[key], img)
                sleep(1)
            else:
                print('Image %s exists.' % img)
    return file


if __name__ == '__main__':
#    url = 'https://www.kijiji.ca/v-apartments-condos/mississauga-peel-region/basement-2bed-mississauga-l5r2e7-bristol-hurontario-1950pm/1646922156'
#    methods = ['requests', 'requests_html', 'selenium']
#    for method in methods:
#        print(f'Getting page with {method}...')
#        start = time()
#        rtext = get_page(url, method, tts=0)
#        end = time()
#        diff = end - start
#        print('took %.2f secs to process' % (diff))
#        soup = BeautifulSoup(rtext, 'html.parser')
#        print(f'found {len(soup.find_all('img'))} pics')
#        print(soup.find_all('div', class_='_1qsawv5'))
    pass
