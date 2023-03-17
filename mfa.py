import multiprocessing as mp
from time import time
import json
import surfer as sf


def init_listener():
    manager = mp.Manager()
    q = manager.Queue()
    process = mp.Process(target=listener, args=(q,))
    process.start()
    return q, process


def listener(q):
    '''listens for messages on the q, writes to file. '''
    while 1:
        mes, file = q.get()
        if mes == 'kill' and file == '':
            break
        with open(file, 'a') as fp:
            json.dump([mes], fp)
            fp.write('\n')
            fp.flush()


def stats(results, tt):
    err = sum([1 for res, t in results if not res])
    total = sum([t for res, t in results if res]) 
    num = len(results)
    print("Data finished processing.")
    print("Total time taken: %.2f secs" % tt)
    print("Success rate: %.2f%%" % ((num-err)/num*100))
    print("Avg time: %.2f secs" % (total/(num-err)))


def mfa(wargs, worker, q=None):
    # must use Manager queue here, or will not work
    kill = False
    if not q:
        kill = True
        manager = mp.Manager()
        q = manager.Queue()
    # put listener to work first
    wargs = [(*args, q) for args in wargs]
    chsz = len(wargs)//4
    print(f"chunksize is {chsz}")
    with mp.Pool() as pool:
        if kill:
            pool.apply_async(listener, args=(q,))
        jobs = pool.imap_unordered(worker, wargs, chunksize=chsz)
        
        # collect results from the workers through the pool result queue
        start = time()
        results = []
        for job in jobs: 
            results.append(job)
        diff = time() - start
        stats(results, diff)

        #now we are done, kill the listener
        if kill:
            q.put(('kill', ''))

