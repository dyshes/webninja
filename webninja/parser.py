import re
import json
import os
import sys
from time import sleep
from . import reader
from . import surfer as sf
from . import bandit as bd
from . import profiler as pf
from . import documenter as doc
from math import inf
from .mfa import init_listener, mfa
from . import phone_server as phs
from bs4 import BeautifulSoup
from .constant import _const  # constant protection
sys.modules[__name__] = _const()
import __main__ as const


def main(ops):
    q, listener = init_listener()
    process("", "", None, ops, q)
    q.put(('kill', ''))
    listener.join()


def setup():
    import __main__ as const
    if len(sys.argv) != 2:
        print("Usage: python3 src/parser.py [conf file]")
        sys.exit()
    ops = doc.read_json(sys.argv[1])
    print(json.dumps(ops, indent=2))
    try:
        const.FOLD = ops[0]['folder']
    except:
        print("Folder not found, setting to default")
        const.FOLD = 'default'
    doc.inc('json')
    os.system('mkdir files &>/dev/null')
    os.system(f'mkdir files/{const.FOLD} &>/dev/null')
    return ops


def get_file(file, ex=""):
    if not file:
        return ""
    fold = f'files/{const.FOLD}'
    f = (fold, file)
    return doc.ftb(f, ext='json', extra=ex)


def process(url, html, drv, ops, q):
    ret = []
    prev_op = {}
    for op in ops:
        b = '' if 'by' not in op else op['by']
        l = [] if 'loc' not in op else op['loc']
        fl = '' if 'file' not in op else op['file']
        crr = [] if 'curr' not in op else op['curr']
        d = inf if 'depth' not in op else op['depth']
        cnc = False if 'conc' not in op else op['conc']
        o = [] if 'ops' not in op else op['ops']
        prev = False if 'prev' not in op else op['prev']
        o = [prev_op] if prev and not o else o
        info = (b, l, fl, crr, d, cnc, o)
        if op['do'] == "next":
            do_next(url, html, drv, q, info)
        elif op['do'] == "rep":
            do_rep(url, html, drv, q, info)
        elif op['do'] == "link":
            do_link(url, html, drv, q, info)
        elif op['do'] == "sleep":
            sleep(op['for'])
        elif op['do'] == "group":
            ret += do_group(url, html, drv, q, info)
        elif op['do'] == "get":
            ret += [do_get(url, html, drv, q, info)]
        elif op['do'] == "go":
            url, html, drv = do_go(url, html, drv, q, info)
        elif op['do'] == "click":
            url, html, drv = do_click(url, html, drv, q, info)
        elif op['do'] == "post":
            url, html, drv = do_post(url, html, drv, q, info)
        elif op['do'] == "server":
            url, html, drv = do_server(url, html, drv, q, info)
        else:
            print(f"Can't perform {op}")
        prev_op = op
    return ret


def do_next(url, html, drv, q, info):
    by, loc, _, curr, d, _, ops = info
    seen = []
    while True:
        nl, cp = reader.page_info(html, loc, curr)
        print(f"Currently on page {cp}")
        process(url, html, drv, ops, q)
        if not nl or int(cp) >= d or cp in seen:
            break
        seen.append(cp)
        url = sf.get_domain(url) + nl
        html, drv = bd.start(url, by, drv)
    drv.close()


def do_rep(url, html, drv, q, info):
    def worker(tup):
        url, info, q = tup
        by, _, _, _, _, _, ops = info
        html, drv = bd.start(url, by)
        process(url, html, drv, ops, q)
        bd.alive(drv) and drv.close()

    bd.alive(drv) and drv.close()
    by, _, file, _, d, conc, ops = info
    ls = doc.read_json(get_file(file))
    ls = pf.remove_duplicates(ls)
    ls = ls if d == inf else ls[:d]
    print(f"{len(ls)} links in {get_file(file)}")
    if conc and by == "firefox":
        args = [(l, info) for l in ls]
        mfa(args, worker, q)
    else:
        args = [(l, info, q) for l in ls]
        [worker(arg) for arg in args]


def do_link(url, html, drv, q, info):
    def worker(tup):
        pfl, info, q = tup
        by, loc, file, _, _, _, ops = info
        if loc not in pfl:
            return
        if not sf.get_domain(pfl[loc]):
            return
        url = pfl[loc]
        html, drv = bd.start(url, by)
        rs = process(url, html, drv, ops, q)
        bd.alive(drv) and drv.close()
        pfl[pfl[loc]] = rs
        q.put((pfl, get_file(file, 'lkd')))

    bd.alive(drv) and drv.close()
    by, loc, file, _, d, conc, ops = info
    pfls = doc.read_json(file)
    pfls = pf.remove_duplicates(pfls)
    pfls = pfls if d == inf else pfls[:d]
    print(f"{len(pfls)} links in {get_file(file)}")
    if conc and by == "firefox":
        args = [(p, info) for p in pfls]
        mfa(args, worker, q)
    else:
        args = [(p, info, q) for p in pfls]
        [worker(arg) for arg in args]


def do_group(url, html, drv, q, info):
    _, loc, file, _, _, _, ops = info
    if not loc:
        loc = ['html', {}]
    cont, attrs = loc
    soup = BeautifulSoup(html, 'html.parser')
    soups = soup.find_all(cont, attrs=attrs)
    profiles = []
    for soup in soups:
        html = soup.prettify()
        profile = {}
        dets = process(url, html, drv, ops, q)
        for det in dets:
            profile = {**profile, **det}
        if file:
            q.put((profile, get_file(file)))
        profiles.append(profile)
    return profiles


def do_get(url, html, drv, q, info):
    name, loc, file, _, _, _, ops = info
    items = reader.page_item(html, loc)[0]
    num = reader.page_item(html, loc)[1]
    clean = []
    for item in items:
        for op in ops:
            if 'extract' in op:
                reg = op['extract']
                m = re.search(reg, item)
                item = m.group() if m else ""
            elif 'replace' in op:
                old, new = op['replace']
                item = item.replace(old, new)
            elif 'strip' in op:
                strip = op['strip']
                item = item.strip(strip)
            elif 'add' in op:
                add = op['add']
                item = add + item
            else:
                print(f"Can't do {op} within get")
        if file:
            q.put((item, get_file(file)))
        clean.append(item)
    profile = reader.profile_generator(clean, num, name)
    return profile


def do_go(url, html, drv, q, info):
    by, loc, _,  _, _, _, ops = info
    html, drv = bd.start(loc, by, drv)
    url = drv.current_url
    process(url, html, drv, ops, q)
    return url, html, drv


def do_click(url, html, drv, q, info):
    by, loc, _, _, _, _, ops = info
    if not drv or not bd.alive(drv):
        html, drv = bd.start(url, by, drv)
    html, drv = bd.click(drv, loc)
    process(url, html, drv, ops, q)
    return url, html, drv


def do_post(url, html, drv, q, info):
    by, loc, file, _, _, _, ops = info
    if not drv or not bd.alive(drv):
        html, drv = bd.start(url, by, drv)
    html, drv = bd.post(drv, loc, file)
    process(url, html, drv, ops, q)
    return url, html, drv


def do_server(url, html, drv, q, info):
    by, loc, file, _, _, _, ops = info
    code = phs.start()
    if not drv or not bd.alive(drv):
        html, drv = bd.start(url, by, drv)
    html, drv = bd.post(drv, loc, code)
    process(url, html, drv, ops, q)
    return url, html, drv


if __name__ == "__main__":
    ops = setup()
    main(ops)
