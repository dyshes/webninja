import pytest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from profiler import _get_price, link_filter, price_filter
from profiler import homogenize, get_keys, map_profile

def test_get_price():
    # Test case 1: Extracting price from a string with a valid price format
    price_string = 'The price is $19.99'
    pattern = r'\$(\d+)\.?(\d{2})'
    groups = 2
    expected = 1999
    result = _get_price(price_string, pattern, groups)
    assert result == expected

    # Test case 2: Extracting price from a string with multiple prices
    price_string = 'The price is $19.99 but the sale price is $9.99'
    pattern = r'\$(\d+)\.?(\d{2})'
    groups = 2
    expected = 1999
    result = _get_price(price_string, pattern, groups)
    assert result == expected

    # Test case 3: Extracting price from a string with no prices
    price_string = 'The item is currently out of stock'
    pattern = r'\$(\d+)\.?(\d{2})'
    groups = 2
    expected = -1
    result = _get_price(price_string, pattern, groups)
    assert result == expected

    # Test case 4: Extracting price from a string with an invalid price format
    price_string = 'The price is 19.99 dollars'
    pattern = r'\$(\d+)\.?(\d{2})'
    groups = 2
    expected = -1
    result = _get_price(price_string, pattern, groups)
    assert result == expected

    # Test case 5: Extracting price from a string with different price format
    price_string = 'The price is $19,99'
    pattern = r'\$(\d+),?(\d{2})'
    groups = 2
    expected = 1999
    result = _get_price(price_string, pattern, groups)
    assert result == expected

    # Test case 6: Extracting price from a string with a price format that includes currency symbol
    price_string = 'The price is €19.99'
    pattern = r'(?:€|\$)(\d+)\.?(\d{2})'
    groups = 2
    expected = 1999
    result = _get_price(price_string, pattern, groups)
    assert result == expected

    # Test case 7: Extracting price from a string with a price format that includes comma
    price_string = 'The price is 19,999.99'
    pattern = r'(\d+),(\d+)\.?(\d{2})'
    groups = 3
    expected = 1999999
    result = _get_price(price_string, pattern, groups)
    assert result == expected

    # Test case 8: Extracting price from a string with a price format that includes decimal point
    price_string = 'The price is 19.999,99'
    pattern = r'(\d+)\.(\d+),(\d{2})'
    groups = 3
    expected = 1999999
    result = _get_price(price_string, pattern, groups)
    assert result == expected


def test_link_filter():
    # Test case 1: 'link' is a key in the dictionary and the value does not match the regular expression
    my_dict = {'link': 'https://www.example.com'}
    pattern = 'https://www\\..*\\.com'
    expected = False
    result = link_filter(my_dict, pattern)
    assert result == expected

    # Test case 2: 'link' is not a key in the dictionary
    my_dict = {'url': 'https://www.example.com'}
    pattern = 'https://www\\..*\\.com'
    expected = False
    result = link_filter(my_dict, pattern)
    assert result == expected

    # Test case 3: 'link' is a key in the dictionary and the value matches the regular expression
    my_dict = {'link': 'http://www.example.com'}
    pattern = 'https://www\\..*\\.com'
    expected = True
    result = link_filter(my_dict, pattern)
    assert result == expected

    # Test case 4: 'link' is a key in the dictionary and the value matches the regular expression with multiple groups
    my_dict = {'link': 'https://www.example.com/path1/path2'}
    pattern = 'https://www\\..*\\.com/(.*)/(.*)'
    expected = False
    result = link_filter(my_dict, pattern)
    assert result == expected

    # Test case 5: 'link' is a key in the dictionary and the value matches the regular expression with multiple groups
    my_dict = {'link': 'https://www.example.com/path1/path2'}
    pattern = 'https://www\\..*\\.com/path1/.*'
    expected = False
    result = link_filter(my_dict, pattern)
    assert result == expected

    # Test case 6: 'link' is a key in the dictionary and the value matches the regular expression with multiple groups
    my_dict = {'link': 'https://www.example.com/path1/path2'}
    pattern = 'https://www\\..*\\.com/path2/.*'
    expected = True
    result = link_filter(my_dict, pattern)
    assert result == expected

    # Test case 7: 'link' is a key in the dictionary and the value matches the regular expression with multiple groups
    my_dict = {'link': 'https://www.example.com/path1/path2'}
    pattern = 'https://www\\..*\\.com/path2/.*'
    expected = True
    result = link_filter(my_dict, pattern)
    assert result == expected

    # Test case 8: 'link' is a key in the dictionary and the value matches the regular expression with multiple groups
    my_dict = {'link': 'https://www.example.com/path1/path2/path3'}
    pattern = 'https://www\\..*\\.com/path1/.*/path3'
    expected = False
    result = link_filter(my_dict, pattern)
    assert result == expected


def test_price_filter():
    # Test case 1: 'price' is a key in the dictionary and the value is less than the integer argument
    my_dict = {'price': '$19.99'}
    price_limit = 2000
    pattern = r'(?:\$|€)(\d+)\.?(\d{2})'
    groups = 2
    expected = True
    result = price_filter(my_dict, price_limit, pattern, groups)
    assert result == expected

    # Test case 2: 'price' is not a key in the dictionary
    my_dict = {'cost': '$19.99'}
    price_limit = 2000
    pattern = r'(?:\$|€)(\d+)\.?(\d{2})'
    groups = 2
    expected = False
    result = price_filter(my_dict, price_limit, pattern, groups)
    assert result == expected

    # Test case 3: 'price' is a key in the dictionary and the value is greater than the integer argument
    my_dict = {'price': '$21.99'}
    price_limit = 2000
    pattern = r'(?:\$|€)(\d+)\.?(\d{2})'
    groups = 2
    expected = False
    result = price_filter(my_dict, price_limit, pattern, groups)
    assert result == expected

    # Test case 4: 'price' is a key in the dictionary and the value is equal to the integer argument
    my_dict = {'price': '$20.00'}
    price_limit = 2000
    pattern = r'(?:\$|€)(\d+)\.?(\d{2})'
    groups = 2
    expected = True
    result = price_filter(my_dict, price_limit, pattern, groups)

    # Test case 5: 'price' is a key in the dictionary and the value is a non-numeric string
    my_dict = {'price': 'Free'}
    price_limit = 2000
    pattern = r'(?:\$|€)(\d+)\.?(\d{2})'
    groups = 2
    expected = True
    result = price_filter(my_dict, price_limit, pattern, groups)
    assert result == expected

    # Test case 6: 'price' is a key in the dictionary and the value is a non-numeric string
    my_dict = {'price': 'N/A'}
    price_limit = 2000
    pattern = r'(?:\$|€)(\d+)\.?(\d{2})'
    groups = 2
    expected = True
    result = price_filter(my_dict, price_limit, pattern, groups)
    assert result == expected

    # Test case 7: 'price' is a key in the dictionary and the value is a non-numeric string
    my_dict = {'price': 'Out of stock'}
    price_limit = 2000
    pattern = r'(?:\$|€)(\d+)\.?(\d{2})'
    groups = 2
    expected = True
    result = price_filter(my_dict, price_limit, pattern, groups)
    assert result == expected


def test_homogenize():
    # Test case 1: Check if all dictionaries have the same keys in the same order
    dict_list = [{'name': 'John', 'age': 25, 'gender': 'male'},
                 {'name': 'Jane', 'age': 22, 'gender': 'female'},
                 {'name': 'Bob', 'age': 30, 'gender': 'male'}]
    expected = [{'name': 'John', 'age': 25, 'gender': 'male'},
                {'name': 'Jane', 'age': 22, 'gender': 'female'},
                {'name': 'Bob', 'age': 30, 'gender': 'male'}]
    result = homogenize(dict_list)
    assert result == expected

    # Test case 2: Check if missing keys are added with empty values
    dict_list = [{'name': 'John', 'age': 25, 'gender': 'male'},
                 {'name': 'Jane', 'age': 22},
                 {'name': 'Bob', 'gender': 'male'}]
    expected = [{'name': 'John', 'age': 25, 'gender': 'male'},
                {'name': 'Jane', 'age': 22, 'gender': ''},
                {'name': 'Bob', 'age': '', 'gender': 'male'}]
    result = homogenize(dict_list)
    assert result == expected

    # Test case 3: Check if empty list returns empty list
    dict_list = []
    expected = []
    result = homogenize(dict_list)
    assert result == expected


def test_get_keys():
    # Test case 1: Check if keys that match the regex are returned
    data = {'name': 'John', 'age': 25, 'gender': 'male', 'address': '123 Main St.'}
    pattern = r'^[a-z]+$'
    expected = ['name', 'age', 'gender', 'address']
    result = get_keys(pattern, data)
    assert result == expected

    # Test case 2: Check if empty list is returned when no keys match the regex
    data = {'123': 'John', '456': 25, '789': 'male'}
    pattern = r'^[a-z]+$'
    expected = []
    result = get_keys(pattern, data)
    assert result == expected

    # Test case 3: Check if empty list is returned when input dict is empty
    data = {}
    pattern = r'^[a-z]+$'
    expected = []
    result = get_keys(pattern, data)
    assert result == expected

    # Test case 4: Check if all keys are returned when regex is None
    data = {'name': 'John', 'age': 25, 'gender': 'male', 'address': '123 Main St.'}
    pattern = ''
    expected = ['name', 'age', 'gender', 'address']
    result = get_keys(pattern, data)
    assert result == expected

    # Test case 5: Check if keys that match the regex are returned even if they have numbers in them
    data = {'name1': 'John', 'age': 25, 'gender2': 'male', 'address3': '123 Main St.'}
    pattern = r'^[a-z]+[0-9]$'
    expected = ['name1', 'gender2', 'address3']
    result = get_keys(pattern, data)
    assert result == expected

    # Test case 6: Check if keys that match the regex are returned even if they have special characters in them
    data = {'name!': 'John', 'age': 25, 'gender@': 'male', 'address#': '123 Main St.'}
    pattern = r'^[a-z]+[!@#$%^&*]$'
    expected = ['name!', 'gender@', 'address#']
    result = get_keys(pattern, data)
    assert result == expected

    # Test case 7: Check if keys that match the regex are returned even if they have uppercase letters in them
    data = {'nameA': 'John', 'age': 25, 'genderB': 'male', 'addressC': '123 Main St.'}
    pattern = r'^[a-z]+[A-Z]$'
    expected = ['nameA', 'genderB', 'addressC']
    result = get_keys(pattern, data)
    assert result == expected


def test_map_profile():
    # Test Case 1
    profile = {'name': 'John Doe', 'age': '30', 'city': 'New York'}
    map_dict = {'name': r'\w+', 'age': r'\d+', 'city': r'\w+'}
    assert map_profile(profile, map_dict) == {'name': 'John', 'age': '30', 'city': 'New'}

    # Test Case 2
    profile = {'name': 'John Doe', 'age': '30', 'city': 'New York'}
    map_dict = {'name': r'\w+', 'age': r'\d+'}
    assert map_profile(profile, map_dict) == {'name': 'John', 'age': '30', 'city': 'New York'}

    # Test Case 3
    profile = {'name': 'John Doe', 'age': '30', 'city': 'New York', 'gender': 'male'}
    map_dict = {'name': r'\w+', 'age': r'\d+', 'city': r'\w+'}
    assert map_profile(profile, map_dict) == {'name': 'John', 'age': '30', 'city': 'New', 'gender': 'male'}

    # Test Case 1
    profile = {'name': 'John Doe', 'age': '30', 'location': 'New York'}
    map_dict = {'name': '([A-Za-z ]+)', 'age': '(\\d+)', 'location': '([A-Za-z ]+)'}
    assert map_profile(profile, map_dict) == {'name': 'John Doe', 'age': '30', 'location': 'New York'}

    # Test Case 2
    profile = {'name': 'Jane Smith', 'age': '25', 'location': 'Los Angeles'}
    map_dict = {'name': '([A-Za-z ]+)', 'age': '(\\d+)'}
    assert map_profile(profile, map_dict) == {'name': 'Jane Smith', 'age': '25', 'location': 'Los Angeles'}

    # Test Case 3
    profile = {'name': 'Bob', 'age': '35', 'location': 'Chicago', 'gender': 'male'}
    map_dict = {'name': '([A-Za-z]+)', 'age': '(\\d+)', 'gender': '([A-Za-z]+)'}
    assert map_profile(profile, map_dict) == {'name': 'Bob', 'age': '35', 'location': 'Chicago', 'gender': 'male'}

    # Test Case 4
    profile = {'name': 'Alice', 'age': '28', 'location': 'San Francisco', 'gender': 'female', 'gender_1':'male'}
    map_dict = {'name': '([A-Za-z ]+)', 'gender': '([A-Za-z]+)'}
    assert map_profile(profile, map_dict) == {'name': 'Alice', 'age': '28', 'location': 'San Francisco', 'gender': 'female', 'gender_1':'male'}

    profile = {'name': 'John Doe', 'age': '30', 'city': 'New York'}
    map_dict = {}
    assert map_profile(profile, map_dict) == {'name': 'John Doe', 'age': '30', 'city': 'New York'}
