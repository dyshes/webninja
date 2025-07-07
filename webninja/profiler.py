import re


def _get_price(pstr, preg, pgrp):
    m = re.search(preg, pstr)
    if not m:
        return -1
    price = ''
    for i in range(1, pgrp + 1):
        price += m.group(i)
    return int(price)


def get_price(profile, preg, pgrp):
    if 'price' not in profile:
        return -1
    pstr = profile['price']
    p = _get_price(pstr, preg, pgrp)
    return p 
        

def confirm(wtc, mes):
    if wtc:
        print(mes)
        return True
    return False  
        
        
def link_filter(pf, reg):
    if confirm("link" not in pf, f"No link in {pf}"):
        return False
    m = re.search(reg, pf['link'])
    r = confirm(m, f"Link contains word {m.group() if m else ''}")
    return not r

        
def price_filter(pf, maxp, preg, pgrp):
    if confirm("price" not in pf, f"No price in {pf}"):
        return False
    price = get_price(pf, preg, pgrp)
    r = confirm(price > maxp, f"{price} is too exp")
    return not r


def homogenize(profiles):
    keys = [key for sub in profiles for key in sub]
    keys = [*set(keys)]
    keys = sorted(keys)
    homo_profiles = []
    for pf in profiles:
        tmp = {}
        for k in keys:
            tmp[k] = pf[k] if k in pf else ''
        homo_profiles.append(tmp)
    return homo_profiles


def get_keys(reg, pf, oth=False):
    keys = [key for key in pf if re.search(reg,key)] 
    other = [key for key in pf if not re.search(reg,key)]
    if oth:
        return other
    return keys


def remove_duplicates(prfs):
    r = []
    for prf in prfs:
        if prf not in r:
            r.append(prf)
    return r 


def map_profile(profile, map_dict):
    new_profile = profile.copy()
    for pkey, pvalue in profile.items():
        for mkey, mvalue in map_dict.items():
            m = re.search(mkey, pkey)
            if m:
                new_value = re.search(mvalue, pvalue).group()
                new_profile[pkey] = new_value
    return new_profile

