import pytest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from mfa import mfa, listener
import documenter as doc
import time
import multiprocessing as mp


def worker(data):
    print(data)
    string, num, file, q = data
    start = time.time()
    result = string * num
    q.put((result, file))
    return True, time.time() - start


def init_listener():
    manager = mp.Manager()
    q = manager.Queue()
    process = mp.Process(target=listener, args=(q,))
    process.start()
    return q, process


def test_mfa():
    wargs = [('a',1), ('b',2), ('c',3), ('d',4)]
    file = 'tests/test_file_4.txt'
    wargs = [arg+(file,) for arg in wargs]
    with open(file, 'w') as fp:
        fp.write('')
    mfa(wargs, worker)
    results = doc.read_json(file)
    assert len(results) == 4

    wargs = [('a',1), ('b',2), ('c',3), ('d',4), ('e', 5)]
    wargs = [arg+(file,) for arg in wargs]
    with open(file, 'w') as fp:
        fp.write('')
    q, lisproc = init_listener()
    mfa(wargs, worker, q)
    q.put(('lol', file))
    q.put(('kill', ''))
    results = doc.read_json(file)
    lisproc.join()
    assert len(results) == 6
    assert lisproc.is_alive() == False
