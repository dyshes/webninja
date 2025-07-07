import pytest
from bs4 import BeautifulSoup
from webninja.reader import _get_strings, _get_mems
from webninja.reader import profile_generator, base_exp
from webninja.reader import get_detail


@pytest.fixture
def htmls():
    return [
        """<html></html>""",
        """
            <html>
                <div id='price'> 100 \n</div>
                <a id='name' href='https://shmoogle.com'></a>
            </html>
        """,
        """
            <html>
                <div id='name'>asldjkf</div>
                <div id='price'>100</div>
                <div id='price'>200</div>
                <div id='price'>
                    <span>300</span>
                </div>
            </html>
        """,
        """
            <html>
                <a href='https://www.youtube.com'></a>
                <a id='Kate' href='http://kate.com'></a>
                <img src="https://sldkf.sdfdh.slkj.com"></img>
            </html>
        """]


@pytest.fixture
def soup():
    soup = BeautifulSoup('''
        <html>
        <head>
            <title>Test Page</title>
        </head>
        <body>
            <div class="container">
                <p>Hello World!</p>
                <p>How are you?</p>
                <div class="subcontainer" id="sub1">
                    <p>I am fine, thank you.</p>
                    <p>How about you?</p>
                </div>
                <div class="subcontainer" id="sub2">
                    <p>I am also fine, thank you.</p>
                </div>
            </div>
            <div class="container">
                <p>This is another container</p>
            </div>
        </body>
        </html>
        ''', 'html.parser')
    return soup


@pytest.fixture
def comp():
    soup = BeautifulSoup('''
    <html>
    <head>
        <title>Test Page</title>
    </head>
    <body>
        <div class="container" id="content1">
            <p class="p1">Hello World!</p>
            <p class="p2">How are you?</p>
            <div class="subcontainer" id="sub1">
                <p class="p3">I am fine, thank you.</p>
                <p class="p4">How about you?</p>
            </div>
            <div class="subcontainer" id="sub2">
                <p class="p5">I am also fine, thank you.</p>
            </div>
        </div>
        <div class="container" id="content2">
            <p class="p6">This is another container</p>
        </div>
        <div class="container" id="content3">
            <p class="p7">This is the last container</p>
        </div>
    </body>
    </html>
    ''', 'html.parser')
    return soup


def test_get_strings(htmls):
    ass = [[],['100'], ['100', '200', '300'], []] 
    for i in range(len(htmls)):
        soup = BeautifulSoup(htmls[i], 'html.parser')
        strs = _get_strings(soup, "div", {'id':'price'})
        assert strs == ass[i]


def test_get_mems(htmls, comp):
    ass = [[],
           ["https://shmoogle.com"], 
           [],
           ["https://www.youtube.com",
            "http://kate.com"]]
    for i in range(len(htmls)):
        soup = BeautifulSoup(htmls[i], 'html.parser')
        strs = _get_mems(soup, "a", {}, "href")
        assert strs == ass[i]
    ass = [[], ['name'], [], ['Kate']]
    for i in range(len(htmls)):
        soup = BeautifulSoup(htmls[i], 'html.parser')
        strs = _get_mems(soup, "a", {}, "id")
        assert strs == ass[i]
    soup = comp
    # Test case 1: Extracting id of all div with class container
    args = ['div', {'class': 'container'}, 'id']
    expected = ['content1', 'content2', 'content3']
    result = _get_mems(soup, *args)
    assert result == expected

    # Test case 2: Extracting class of all p tags
    args = ['p', {}, 'class']
    expected = ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7']
    result = _get_mems(soup, *args)
    assert result == expected

    # Test case 3: Extracting id of all div with class subcontainer
    args = ['div', {'class': 'subcontainer'}, 'id']
    expected = ['sub1', 'sub2']
    result = _get_mems(soup, *args)
    assert result == expected

    # Test case 4: Extracting class of all div with class container
    args = ['div', {'class': 'container'}, 'class']
    expected = ['container', 'container', 'container']
    result = _get_mems(soup, *args)
    assert result == expected

    # Test case 5: Extracting class of div with class non-existent
    args = ['div', {'class': 'non-existent'}, 'class']
    expected = []
    result = _get_mems(soup, *args)
    assert result == expected

    # Test case 6: Extracting id of all div with class container and subcontainer
    args = ['div', {'class': ['container', 'subcontainer']}, 'id']
    expected = ['content1', 'sub1', 'sub2', 'content2', 'content3']
    result = _get_mems(soup, *args)
    assert result == expected

    # Test case 7: Extracting class of all div with class container and subcontainer
    args = ['div', {'class': ['container', 'subcontainer']}, 'class']
    expected = ['container', 'subcontainer', 'subcontainer', 'container', 'container']
    result = _get_mems(soup, *args)
    assert result == expected

    # Test case 8: Extracting id of all div with id content1 and content2
    args = ['div', {'id': ['content1', 'content2']}, 'id']
    expected = ['content1', 'content2']
    result = _get_mems(soup, *args)
    assert result == expected

    # Test case 9: Extracting class of all div with id content1 and content2
    args = ['div', {'id': ['content1', 'content2']}, 'class']
    expected = ['container', 'container']
    result = _get_mems(soup, *args)
    assert result == expected

    # Test case 10: Extracting class of all div with id non-existent
    args = ['div', {'id': 'non-existent'}, 'class']
    expected = []
    result = _get_mems(soup, *args)
    assert result == expected


def test_profile_generator():
    dets = [['thing', 'thing', 'thing'],
            ['100'],
            [''],
            []]
    nums = [2, 0, 1, 5]
    ass = [{'key':'thing','key_1':'thing'},
           {},
           {'key':''},
           {}]
    for i in range(len(dets)):
        profile = profile_generator(dets[i],
                nums[i], 'key')
        assert profile == ass[i]
    nums = [100, 0, 100, 0]
    ass = [{'key':'thing', 'key_1':'thing', 'key_2':'thing'},
           {},
           {'key':''},
           {}]
    for i in range(len(dets)):
        profile = profile_generator(dets[i],
                nums[i], 'key')
        assert profile == ass[i]


def test_base_exp(soup):
    # Test case with 5 elements in the list
    args = [-1, 'div', {'class': 'subcontainer'}, 'id']
    expected = ['sub1', 'sub2']
    assert base_exp(soup, args) == (expected, 2)

    # Test case with 4 elements in the list (attributes as dict)
    args = [3, 0, 'p', {}]
    expected = ['Hello World!', 'How are you?', 'I am fine, thank you.']
    assert base_exp(soup, args) == (expected, 3)

    # Test case with 4 elements in the list (attribute as string)
    args = [2, 1, 'div', {'class':'subcontainer'}, 'class']
    expected = ['subcontainer']
    assert base_exp(soup, args) == (expected, 2)

    # Test case with 3 elements in the list
    args = [2, 'p', {}]
    expected = ['Hello World!', 'How are you?']
    assert base_exp(soup, args) == (expected, 2)
    
    # Test case with 4 elements in the list (attributes as dict) and offset
    args = [2, 1, 'div', {'class': 'container'}]
    expected = ['This is another container']
    assert base_exp(soup, args) == (expected, 2)

    # Test case with 4 elements in the list (attributes as dict) and offset
    args = [1, 1, 'div', {'class': 'container'}]
    expected = ['This is another container']
    assert base_exp(soup, args) == (expected, 1)

    # Test case with 4 elements in the list (attributes as dict) and offset
    args = [3, 1, 'p', {}]
    expected = ['How are you?', 'I am fine, thank you.', 'How about you?']
    assert base_exp(soup, args) == (expected, 3)

    # Test case with 4 elements in the list (attributes as dict) and offset
    args = [2, 2, 'p', {}]
    expected = ['I am fine, thank you.', 'How about you?']
    assert base_exp(soup, args) == (expected, 2)

    # Test case with 3 elements in the list and offset
    args = [1, 'title', {}]
    expected = ['Test Page']
    assert base_exp(soup, args) == (expected, 1)


def test_get_detail(comp):
    soup = comp
    data = [2, 1, 'div', {'class': 'container'},
            [1, 'p', {}, 'class']]
    expected = ['p6', 'p7']
    result = get_detail(soup, data)
    assert result == (expected, 2)

    data = [1, 1, 'div', {'class': 'container'},
            [1, 'p', {}, 'class']]
    expected = ['p6']
    result = get_detail(soup, data)
    assert result == (expected, 1)

    data = [1, 0, 'div', {'class': 'container'},
            [10, 0, 'p', {}, 'class']]
    expected = ['p1', 'p2', 'p3', 'p4', 'p5']
    result = get_detail(soup, data)
    assert result == (expected, 5)
    
    data = [1, 0, 'div', {'class': 'container'},
            [1, 1, 'div', {'class':'subcontainer'},
             [1, 1, 'p', {}, 'class']]]
    expected = []
    result = get_detail(soup, data)
    assert result == (expected, 1)

    data = [5, 0, 'div', {'class': 'subcontainer'},
            [10, 1, 'p', {}, 'class']]
    expected = ['p4']
    result = get_detail(soup, data)
    assert result == (expected, 3)

    result = get_detail(soup, [])
    assert result == ([], 0)

    data = [1, "html", {}]
    result = get_detail(soup, data)
    assert result == ([soup.prettify()], 1)
