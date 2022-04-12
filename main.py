# -*- coding:utf-8 -*-
import requests

def fanyiyoudao(word):

    data = {
        'doctype': 'json',
        'type': 'AUTO',
        'i': word,
    }
    url = "http://fanyi.youdao.com/translate"
    r = requests.get(url, params=data)
    result = r.json()
    print(result['translateResult'][0][0]['tgt'])
    res = result['translateResult'][0][0]['tgt']
    return res


fanyiyoudao("this is secret data")
