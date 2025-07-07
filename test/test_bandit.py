from webninja import bandit


def test_tor_driver():
    try:
        success = True
        for i in range(0, 3):
            drv = bandit.tor_driver()
            drv.close()
    except:
        success = False
    assert success == True


def test_firefox_driver():
    try:
        success = True
        for i in range(0, 3):
            drv = bandit.firefox_driver()
            assert drv != None
            drv.close()
    except:
        success = False
    assert success == True


def test_checking_ip_address():
    ipstr = bandit.checking_ip_address()
    assert ipstr != ""


def test_load_page():
    try:
        html = bandit.load_page('http://www.example.com')
    except:
        html = ""
    assert html != ""


def test_get_google_page():
    try:
        success = True
        url = 'https://google.com/search?q=earths+radius'
        drv = bandit.tor_driver()
        html, drv = bandit.get_google_page(url, drv)
        drv.close()
    except:
        success = False
    assert success == True


