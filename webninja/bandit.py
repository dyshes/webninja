from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options as options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep, time
from bs4 import BeautifulSoup
from . import surfer as sf
from .mfa import mfa
from . import documenter as doc
from .reader import view_extractor as read
from . import profiler
import re


def start(url, by, drv=None):
    dom = sf.get_domain(url)
    google = re.search(r"google", dom)
    html = ''
    if not by and not drv:
        return sf.get_page(url), None
    if not alive(drv):
        drv = get_driver(by)
    if by == 'google':
        html, drv = get_google_page(url, drv)
    elif by == 'tor' and google:
        html, drv = get_google_page(url, drv)
    elif by == 'tor' or by == 'firefox':
        html, drv = load_page(url, drv)
    else:
        print(f"Can\'t get {url} by {by}")
    return html, drv


def get_driver(by):
    if by == 'google' or by == "tor":
        return tor_driver()
    elif by == 'firefox':
        return firefox_driver()
    return None


def alive(drv):
    try:
        drv.title
        return True
    except:
        return False


def tor_driver():
    binary_path = '/Applications/Tor Browser.app'\
        '/Contents/MacOS/firefox'
    driver_path = '/usr/local/bin/geckodriver/'
    ops = options()
    ops.binary_location = binary_path
    ops.headless = False
    serv = Service(driver_path)
    print('Setting up driver...')
    driver = webdriver.Firefox(service=serv, options=ops)
    sleep(2)
    print('Connecting...')
    con_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH,
            '//*[@id="connectButton"]')))
    ActionChains(driver)\
        .move_to_element(con_button)\
        .click(con_button)\
        .perform()
    sleep(6)
    print('Connection Established.')
    return driver


def firefox_driver():
    ops = options()
    ops.headless = False
    return webdriver.Firefox(options=ops)


def checking_ip_address():
    print('Checking IP address...')
    driver = tor_driver()
    driver.get('https://check.torproject.org/')
    sleep(3)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    ipstr = soup.find_all('strong')[0].string
    print('Your IP address is: {}'.format(ipstr))
    driver.close()
    return ipstr


def login(url, user_xpath, username,
          pass_xpath, password, submit_xpath):
    # login to reddit
    browser = firefox_driver()
    browser.get(url)
    browser.implicitly_wait(10)
    sleep(2)
    user_field = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH,
            user_xpath)))
    pass_field = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH,
            pass_xpath)))
    submit = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH,
            submit_xpath)))
    browser.execute_script("arguments[0].scrollIntoView();",
        user_field)
    ActionChains(browser)\
        .move_to_element(user_field)\
        .click(user_field)\
        .send_keys(username)\
        .perform()
    browser.execute_script("arguments[0].scrollIntoView();",
        pass_field)
    ActionChains(browser)\
        .move_to_element(pass_field)\
        .click(pass_field)\
        .send_keys(password)\
        .perform()
    browser.execute_script("arguments[0].scrollIntoView();",
        submit)
    ActionChains(browser)\
        .move_to_element(submit)\
        .click(submit)\
        .perform()
    sleep(40)
    html = browser.page_source
    return html, browser


def search(url, search_xpath, thing, submit_xpath):
    driver = webdriver.Firefox()
    driver.get(url)
    driver.implicitly_wait(10)
    sleep(2)
    search_field = WebDriverWait(driver,10).until(
        EC.presence_of_element_located((By.XPATH,
            search_xpath)))
    submit = WebDriverWait(driver,10).until(
        EC.presence_of_element_located((By.XPATH,
            submit_xpath)))
    driver.execute_script("arguments[0].scrollIntoView();",
        search_field)
    ActionChains(driver)\
        .move_to_element(search_field)\
        .click(search_field)\
        .send_keys(thing)\
        .perform()
    driver.execute_script("arguments[0].scrollIntoView();",
        submit)
    ActionChains(driver)\
        .move_to_element(submit)\
        .click(submit)\
        .perform()
    sleep(10)
    html = driver.page_source
    return html, driver


def click(drv, xpath):
    bt = WebDriverWait(drv, 10).until(
        EC.presence_of_element_located((
            By.XPATH, xpath)))
    drv.execute_script(
        "arguments[0].scrollIntoView();",
        bt)
    ActionChains(drv)\
        .move_to_element(bt)\
        .click(bt)\
        .perform()
    drv.implicitly_wait(10)
    html = drv.page_source
    return html, drv


def post(drv, xpath, word):
    field = WebDriverWait(drv, 10).until(
        EC.presence_of_element_located((
            By.XPATH, xpath)))
    drv.execute_script("arguments[0].scrollIntoView();",
                       field)
    ActionChains(drv)\
        .move_to_element(field)\
        .click(field)\
        .send_keys(word)\
        .perform()
    drv.implicitly_wait(10)
    html = drv.page_source
    return html, drv


def load_page(url, driver=None, tts=3):
    close = False
    if not driver:
        close = True
        driver = firefox_driver()
    driver.get(url)
    sleep(tts)
    html = driver.page_source
    if close:
        driver.close()
        return html
    return html, driver


def get_google_page(url, driver):
    again = True
    tries = 1
    while again:
        driver.get(url)
        driver.implicitly_wait(10)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        things = soup.find_all('a')
        if len(things) <= 3:
            tries += 1
            driver.close()
            driver = tor_driver()
            continue
        again = False
    print(f"That took {tries} tries")
    return html, driver


def google_pager(url, reader, max_pages=5):
    driver = tor_driver()
    html, driver = get_google_page(url, driver)
    visited = []
    while True:
        nl, cp, meta, file = reader(html)
        if not nl:
            print('No next')
            break
        elif int(cp) >= max_pages:
            print('Hit max')
            break
        elif cp in visited:
            print('Already visited')
            break
        visited.append(cp)
        print('Getting Next Page...')
        url = sf.get_domain(url) + nl
        html, driver = get_google_page(url, driver)
    return meta, file


def pager(url, reader, max_pages=5):
    driver = firefox_driver()
    html, driver = load_page(url, driver)
    visited = []
    while True:
        nl, cp, meta, file = reader(html)
        if not nl:
            print('No next')
            break
        elif int(cp) >= max_pages:
            print('Hit max')
            break
        elif cp in visited:
            print('Already visited')
            break
        visited.append(cp)
        print('Getting Next Page...')
        url = sf.get_domain(url) + nl
        html, driver = load_page(url, driver)
    return meta, file


def link_profile(tup):
    pid, url, pf, vloc, file, q = tup
    print('Getting [%d]...' % pid)
    good = True
    for key in profiler.get_keys(r"link", pf):
        try:
            pf[key] = url + pf[key]
            start = time()
            html = load_page(pf[key])
            end = time()
            view = read(html, vloc)
            linked = {**pf,**view}
        except Exception as e:
            good = False
            end = time()
            print(e)
            print(f'[{pid}] {pf[key]} failed.')
    print(f'[{pid}] has {len(linked)} keys')
    q.put((linked, file))
    return good, end - start


def fast_viewer(infile, url, pfilt, vloc, out):
    profiles = doc.read_json(infile)
    print(f'There are {len(profiles)} profiles')
    filts = [pf for pf in profiles if pfilt(pf)]
    print(f'After filter, {len(filts)} profiles')
    fargs = []
    for i,pf in enumerate(filts):
        fargs.append((i, url, pf, vloc, out))
    mfa(fargs, link_profile)
    return out


