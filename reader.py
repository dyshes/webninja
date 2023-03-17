from bs4 import BeautifulSoup


def _get_strings(soup, el, dct):
    retlst = []
    strels = soup.find_all(el, attrs=dct)
    if not strels:
        return retlst
    for strel in strels:
        retstr = ''
        for string in strel.stripped_strings:
            retstr += string
        retlst.append(retstr)
    return retlst


def _get_mems(soup, el, dct, mem):
    retlst = []
    memels = soup.find_all(el, attrs=dct)
    if not memels:
        return retlst
    for memel in memels:
        if mem in memel.attrs:
            if isinstance(memel.attrs[mem], list):
                retlst.append(memel[mem][0])
            else:
                retlst.append(memel[mem])
    return retlst


def profile_generator(det, num, key):
    keys = [key]
    for i in range(1, num):
        keys.append(f'{key}_{i}')
    common = min(len(det), num)
    profile = {}
    for i in range(0, common):
        profile[keys[i]] = det[i] 
    return profile 


def profile_extractor(soup, pf_loc, details):
    """
    extracts profiles from html page
    :param soup: soup of html page
    :param pf_loc: profile location
    :param details: dict of profile details
    """
    if not pf_loc:
        return []
    pf_cont, pf_attrs = pf_loc
    soups = soup.find_all(pf_cont, attrs=pf_attrs)
    profiles = []
    for soup in soups:
        profile = {}
        for key, det_loc in details.items():
            det, num = get_detail(soup, det_loc)
            detail = profile_generator(det, num, key)
            profile = {**profile, **detail} 
        profiles.append(profile)
    return profiles


def base_exp(soup, exp):
    off = 0
    if len(exp) == 5:
        num, off, cont, attrs, mem = exp
        det = _get_mems(soup, cont, attrs, mem)
    elif len(exp) == 4 and isinstance(exp[-1], dict):
        num, off, cont, attrs = exp
        det = _get_strings(soup, cont, attrs)
    elif len(exp) == 4 and isinstance(exp[-1], str):
        num, cont, attrs, mem = exp
        det = _get_mems(soup, cont, attrs, mem)
    else:
        num, cont, attrs = exp
        if num == 1 and cont == "html" and attrs == {}:
            return [soup.prettify()], 1
        det = _get_strings(soup, cont, attrs)
    num = len(det) if num == -1 or num > len(det) else num
    return det[off: num + off], num


def get_detail(soup, exp):
    if not exp:
        return [], 0
    if not isinstance(exp[-1], list):
        return base_exp(soup, exp)
    else:
        off = 0
        if len(exp) == 5:
            num, off, cont, attrs, sub = exp
        else:
            num, cont, attrs, sub = exp
        soups = soup.find_all(cont, attrs=attrs)
        num = len(soups) if num == -1 else num
        soups = soups[off: num + off]
        det, num = [], 0
        for soup in soups:
            temp = get_detail(soup, sub)
            det += temp[0]
            num += temp[1]
        return det, num


def page_item(html, loc):
    soup = BeautifulSoup(html, 'html.parser')
    lst_item, num = get_detail(soup, loc)
    return lst_item, num


def page_info(html, nl, cp):
    soup = BeautifulSoup(html, 'html.parser')
    lst_cp, _ = get_detail(soup, cp)
    curr_page = lst_cp[0] if lst_cp else '?'
    lst_nl, _ = get_detail(soup, nl)
    next_link = lst_nl[0] if lst_nl else ''
    return next_link, curr_page


def page_extractor(html, page, pf):
    soup = BeautifulSoup(html, 'html.parser')
    cp, nl = page
    # getting current page
    lst_cp, _ = get_detail(soup, cp)
    curr_page = lst_cp[0] if lst_cp else '?'
    # getting next link
    lst_nl, _ = get_detail(soup, nl)
    next_link = lst_nl[0] if lst_nl else ''
    # getting profiles
    loc, info = pf
    profiles = profile_extractor(soup, loc, info)
    return curr_page, profiles, next_link


def view_extractor(html, info):
    soup = BeautifulSoup(html, 'html.parser')
    loc = ["html", {}]
    profiles = profile_extractor(soup, loc, info)
    return profiles[0] if profiles else {}


if __name__ == "__main__":
   import requests
   url = "https://www.olx.kz/d/obyavlenie/stol-transformer-i-kinizhka-IDntbst.html"
   r = requests.get(url)
   soup = BeautifulSoup(r.text, "html.parser")
   print(get_detail(soup, [3, "div",
       {"class": "swiper-zoom-container"},
       [1, "img", {}, "src"]]))
