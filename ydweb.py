#!/usr/bin/env python3

import os
import sys

import requests
from pyquery import PyQuery
from requests.utils import requote_uri

from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory


def getFileHistory():
    d = os.path.expanduser(os.path.join("~", ".cache", "ydweb"))
    if not os.path.exists(d):
        os.makedirs(d)

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

    return s


def get_auth_translation(pq):
    return pq('#authTrans').text()


def get_e_transform(pq):
    return pq('#eTransform').text()


def get_examples(pq):
    return pq('#examples').text()


def get_typo(pq):
    return pq('.error-typo').text()


def search(word):
    verbose_level = word.count('!')
    word = word.replace('!', '')

    url = requote_uri("https://www.youdao.com/w/" + word)
    ret = requests.get(url, timeout=10)
    if ret.status_code != 200:
        print("Status Code: %d" % ret.status_code)
        return None

    ret.encoding = ret.apparent_encoding
    pq = PyQuery(ret.content.decode())

    s = ''
    basic_translate = get_basic_translation(pq)
    if len(basic_translate) > 0:
        s += basic_translate

    if verbose_level >= 1:
        auth_translate = get_auth_translation(pq)
        if auth_translate:
            s += '\n\n' + auth_translate

    if verbose_level >= 2: 
        eTransform = get_e_transform(pq) 
        if eTransform:
            s += '\n\n' + eTransform

    if verbose_level >= 3:
        examples = get_examples(pq)
        if examples:
            s += '\n\n' + examples

    if len(s) == 0:
        error_typo = get_typo(pq)
        if len(error_typo) == 0:
            return None
        
        s = error_typo

    s += '\n' + ('=' * 64) + '\n'
    return s


if __name__ == "__main__":
    history = getFileHistory()

    while True:
        try:
            word = prompt('> ', history=history)
        except (EOFError, KeyboardInterrupt) as e:
            print("Bye!")
            sys.exit(0)

        word = word.strip()
        if not word:
            continue

        try:
            explanation = search(word)
        except:
            msg = str(sys.exc_info()[1])
            print(msg)
            continue

        if explanation is None:
            print("[ERROR] Failed to fetch explanation!")
            continue

        print(explanation)

