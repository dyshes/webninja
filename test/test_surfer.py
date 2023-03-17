import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from surfer import get_domain


def test_get_domain():
    url = 'https://www.example.com/path/to/page'
    ret = get_domain(url)
    assert ret == 'https://www.example.com'

    url = 'https://www.mail.google.com/asd;gj/sfh'
    ret = get_domain(url)
    assert ret == "https://www.mail.google.com"

    url = 'https://google.com'
    ret = get_domain(url)
    assert ret == 'https://google.com'
