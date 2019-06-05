#!/usr/bin/env python3

import os
import sys

import zlib
import pickle

import requests
from requests.utils import requote_uri
from pyquery import PyQuery

import time
from threading import Thread

from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style


def get_root():
    d = os.path.expanduser(os.path.join("~", ".cache", "ydweb"))
    if not os.path.exists(d):
        os.makedirs(d)

    return d


def getFileHistory():
    d = get_root()
    f = os.path.join(d, "word_history.txt")
    history = FileHistory(f)
    return history


def get_basic_translation(pq):
    pq = pq('#phrsListTab')
    s = pq('.wordbook-js').text()

    pq = pq('.trans-container')
    if pq('ul'):
        s += '\n' + pq('ul').text()

    if pq('.additional'):
        s += '\n' + pq('.additional').text()

    if s.find('添加释义') >= 0:
        s = ''

    return s


def get_auth_translation(pq):
    return pq('#authTrans').text()


def get_e_transform(pq):
    return pq('#eTransform').text()


def get_examples(pq):
    return pq('#examples').text()


def get_typo(pq):
    return pq('.error-typo').text()


def load_dict(path):
    data = zlib.decompress(open(path, 'rb').read())
    return pickle.loads(data)


def dump_dict(path, d):
    data = zlib.compress(pickle.dumps(d))
    open(path, 'wb').write(data)


def get_cache_path():
    d = get_root()
    path = os.path.join(d, "dict-cache.pkl")
    return path


def get_dict_cache():
    path = get_cache_path()
    if not os.path.exists(path):
        return {}

    return load_dict(path)


def save_dict_cache(dict_cache):
    path = get_cache_path()
    dump_dict(path, dict_cache)


def get_sys_dict():
    t = os.path.abspath(os.path.realpath(__file__))
    d = os.path.join(os.path.dirname(t), "dict")

    sys_dict = {}

    path_eng = os.path.join(d, "eng.pkl")
    if os.path.exists(path_eng):
        sys_dict.update(load_dict(path_eng))

    path_chn = os.path.join(d, "chn.pkl")
    if os.path.exists(path_chn):
        sys_dict.update(load_dict(path_chn))

    return sys_dict


def search(word):
    url = requote_uri("https://www.youdao.com/w/" + word)
    ret = requests.get(url, timeout=10)
    if ret.status_code != 200:
        print("Status Code: %d" % ret.status_code)
        return None

    ret.encoding = ret.apparent_encoding
    pq = PyQuery(ret.content.decode())

    results = {
        "basic": get_basic_translation(pq), 
        "auth": get_auth_translation(pq),
        "e-transform": get_e_transform(pq),
        "examples": get_examples(pq),
        "typo": get_typo(pq)
    }

    return results
    

def lookup(word, dict_cache, dict_sys):
    verbose_level = word.count('!')
    word = word.replace('!', '').lower()

    if word in dict_cache:
        results = dict_cache[word]
    elif word in dict_sys:
        results = dict_sys[word]
    else:
        results = search(word)
        dict_cache[word] = results

    s = ''
    basic_translate = results["basic"]
    if len(basic_translate) > 0:
        s += basic_translate

    if verbose_level >= 1:
        auth_translate = results["auth"]
        if auth_translate:
            s += '\n\n' + auth_translate

    if verbose_level >= 2: 
        eTransform = results["e-transform"]
        if eTransform:
            s += '\n\n' + eTransform

    if verbose_level >= 3:
        examples = results["examples"]
        if examples:
            s += '\n\n' + examples

    if len(s) == 0:
        error_typo = results["typo"]
        if len(error_typo) == 0:
            return None
        
        s = error_typo

    s += '\n' + ('=' * 64) + '\n'
    return s


def search_and_cache(i, N, word, dict_new):
    print("Job [%d/%d: %s] is running..." % (i, N, word))
    results = search(word)
    dict_new[word] = results
    print("Job [%d/%d: %s] has completed!" % (i, N, word))


def cache_wordlist(f_wordlist, jobs, save_to=None):
    t = open(f_wordlist).read().split("\n")
    t = [w.strip() for w in t]
    wordlist = [w.lower() for w in t if len(w) > 0]
    N = len(wordlist)

    dict_new = {}
    dict_cache = get_dict_cache()
    dict_sys = get_sys_dict()

    jobs_todo = []
    for i, word in enumerate(wordlist):
        if word in dict_cache:
            dict_new[word] = dict_cache[word]
            continue

        if word in dict_sys:
            dict_new[word] = dict_sys[word]
            continue

        t = Thread(target=search_and_cache, args=(i+1, N, word, dict_new))
        jobs_todo.append(t)

    jobs_running = []
    lastUpdateTimestamp = time.time()
    while jobs_todo or jobs_running:
        jobs_running = [j for j in jobs_running if j.is_alive()]

        n = jobs - len(jobs_running)
        for t in jobs_todo[:n]:
            t.daemon = True
            t.start()
            jobs_running.append(t)

        jobs_todo = jobs_todo[n:]
        time.sleep(0.1)

        if time.time() - lastUpdateTimestamp > 60:
            lastUpdateTimestamp = time.time()

            if save_to:
                dump_dict(save_to, dict_new)
                print("Dictionary has been updated.")
            else:
                save_dict_cache({**dict_cache, **dict_new})
                print("Dictionary cache has been updated.")


def get_args():
    import argparse

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter, 
        allow_abbrev=False, prog='ydweb',
        description='Console-based YouDao dictionary'
    )

    parser.add_argument("--wordlist", 
        help="search and cache words in a text file with each word per line"
    )

    parser.add_argument("--save-to", 
        help="path to save the crawled dictionary"
    )

    parser.add_argument("--jobs", type=int, default=os.cpu_count(),
        help="number of jobs to search and cache words in parallel"
    )

    cfg = parser.parse_args()
    return cfg



if __name__ == "__main__":
    cfg = get_args()
    if cfg.wordlist:
        cache_wordlist(cfg.wordlist, cfg.jobs, cfg.save_to)
        sys.exit(0)


    # start a thread that takes care of dict_cache
    dict_sys = None
    dict_cache = None
    lastDictSize = None
    def update_dict_cache():
        global dict_sys
        global dict_cache
        global lastDictSize

        dict_cache = get_dict_cache()
        lastDictSize = len(dict_cache)

        dict_sys = get_sys_dict()

        while True:
            time.sleep(2)
            if len(dict_cache) == lastDictSize:
                continue

            save_dict_cache(dict_cache)
            lastDictSize = len(dict_cache)


    t = Thread(target=update_dict_cache)
    t.daemon = True
    t.start()


    # arguments for prompt
    history = getFileHistory()
    style = Style.from_dict({
        'bottom-toolbar':      'fg:#333333',
        'bottom-toolbar.text': 'bg:#20B2AA',
    })

    def get_bottom_toolbar():
        toolbar = [("bg:#00aa00", "[System] ")]
        if dict_sys is None:
            toolbar += [("", "Loading...")]
        else:
            toolbar += [
                ("bg:#aaaaaa", "%d" % len(dict_sys)),
                ("", " entries")
            ]

        toolbar += [("bg:#00aa00", "        [User] ")]
        if lastDictSize is None:
            toolbar += [("", "Loading...")]
        else:
            toolbar += [
                ("bg:#aaaaaa", "%d" % len(dict_cache)),
                ("", " entries ("),
                ("bg:#aaaaaa", "%d" % lastDictSize),
                ("", " cached)")
            ]

        return toolbar


    # interactive word lookup
    while True:
        try:
            word = prompt('> ', 
                history=history,
                bottom_toolbar=get_bottom_toolbar,
                style=style,
                refresh_interval=0.5
            )
        except KeyboardInterrupt:
            continue
        except EOFError:
            print("Bye!")
            sys.exit(0)

        word = word.strip()
        if not word:
            continue

        # wait until dict_cache is fully loaded
        while dict_cache is None or dict_sys is None:
            time.sleep(0.1)

        try:
            explanation = lookup(word, dict_cache, dict_sys)
        except:
            msg = str(sys.exc_info()[1])
            print(msg)
            continue

        if explanation is None:
            print("[ERROR] Failed to fetch explanation!")
            continue

        print(explanation)

