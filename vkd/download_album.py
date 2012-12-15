#!/usr/bin/env python
# Encoding: utf8
__author__ = 'syabro'

import os, urlparse
import HTMLParser
import json

from configobj import ConfigObj
import requests

from download import download


def download_album(url):
    config = ConfigObj(os.path.expanduser('~/.vkd'))
#    VK_ID = config.get('VK_ID', '3201770')
    VK_ID = config.get('VK_ID')
    VK_AUTH_URL = 'https://oauth.vk.com/authorize'
    VK_API_URL = 'https://api.vk.com/method/%s'
    ACCESS_TOKEN = config.get('ACCESS_TOKEN')

    print 'Downloading from', url
    qs = urlparse.parse_qs(urlparse.urlparse(url).query)
    if 'album_id' not in qs:
        print 'Error: Url doesn\'t album id'
        exit()
    album_id = qs['album_id'][0]
    owner_id = qs['id'][0].lstrip('-')

    if VK_ID is None:
        print u'Вы должны зарегистрировать приложение ВКонтакте для продолжения'
        print u'Это можно сделать по адресу https://vk.com/editapp?act=create'
        print u'Введите ID приложения:',
        VK_ID = raw_input()
        config['VK_ID'] = VK_ID
        config.write()

    if ACCESS_TOKEN is not None:
        response = requests.get(VK_API_URL % 'audio.get', params={
            'access_token': ACCESS_TOKEN,
            'album_id': album_id
        })
        data = json.loads(response.content)
        if 'error' in data:
            ACCESS_TOKEN = None



    if ACCESS_TOKEN is None:
        r = requests.get(VK_AUTH_URL, params={
            'client_id': VK_ID,
            'scope': '9',
            'redirect_uri': 'http://oauth.vk.com/blank.html',
            'display':'page',
            'response_type': 'token'
        })
        print u'Откройте данную ссылку в браузере'
        print r.url
        print u'И разрешите доступ для приложения'
        print u'После чего вставьте полученную ссылку.'
#        url = 'https://oauth.vk.com/blank.html#access_token=01859171515fb49701d4afecb501a950f20019901998a10515d671739d38623b2140d05&expires_in=86400&user_id=1842025'
        print u'Ссылка: '
        url = raw_input()
        params = url.split('#')[1]
        ACCESS_TOKEN = dict(pair.split('=') for pair in params.split('&'))['access_token']
        config['ACCESS_TOKEN'] = ACCESS_TOKEN
        config.write()


    for owner in (None, 'uid', 'gid'):
        params = {
            'access_token': ACCESS_TOKEN,
            'album_id': album_id
        }
        if owner:
            params[owner] = owner_id
        response = requests.get(VK_API_URL % 'audio.get', params=params)
        data = json.loads(response.content)
        if 'error' in data:
            continue
        if data['response']:
            break

    _htmlparser = HTMLParser.HTMLParser()

    if not os.path.exists(album_id):
        os.mkdir(str(album_id))

    print u'Найдено аудиозаписей:', len(data['response'])
    for i, audio in enumerate(data['response']):
        title = _htmlparser.unescape('%s - %s' % (audio['artist'], audio['title']))
        print '%d. %s' % (i+1, title)
        download(audio['url'], album_id, '%s.mp3' % title)


if __name__=='__main__':
    download_album('https://vk.com/audio?album_id=31611664')