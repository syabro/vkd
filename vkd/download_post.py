#!/usr/bin/env python
# Encoding: utf8
from configobj import ConfigObj
import os, shutil
import mutagen
from mutagen.id3 import ID3, TPE2, TCMP, APIC, TAL, TRCK
from bs4 import BeautifulSoup
import requests

import soupselect; soupselect.monkeypatch()
from download import download

config = ConfigObj(os.path.expanduser('~/.vkd'))
itunes_autoimport_dir = config.get('itunes_autoimport_dir', os.path.expanduser('~/Music/iTunes/iTunes Media/Automatically Add to iTunes.localized/'))

def download_post(url):
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.15 (KHTML, like Gecko) Chrome/24.0.1295.0 Safari/537.15'})

    bs = BeautifulSoup(response.text, 'html5lib')
    title = bs.findSelect('a.fw_post_author')[0].text
    try:
        album = bs.findSelect('.wall_post_text')[0].text.split('\n')[0].strip()
    except IndexError:
        album = ''
    album_id = bs.findSelect('.fw_like_count')[0]['id'].replace('like_count','')
    try:
        cover =  bs.findSelect('.page_media_thumb1 img')[0]['src']
    except IndexError:
        cover = None
    print title, '-', album
    songs = [{
        'url': input['value'].split(',')[0],
        'title': bs.findSelect('#audio%s .title_wrap' % input['id'].replace('audio_info', ''))[0].text
        } for input in bs.findSelect('input[type=hidden]') if input.has_key('id') and input['id'].startswith('audio')
    ]

    # Creating folder
    target_dir = os.path.join('/tmp/vk-post-downloader/',album_id)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # Downloading
    print '', title, '-', album_id
    if cover:
        download(cover, target_dir, 'cover.jpg', ' Cover')
        cover_filename = os.path.join(target_dir, 'cover.jpg')

        try:
            from PIL import Image
            image = Image.open(cover_filename)
            size = [min(image.size), min(image.size)]
            background = Image.new('RGBA', size, (255, 255, 255, 0))
            background.paste(
                image,
                ((size[0] - image.size[0]) / 2, (size[1] - image.size[1]) / 2))
            background.save(cover_filename, format='jpeg')
        except ImportError:
            print u'PIL не найден. Вы можете попробовать его установить командой easy_install PIL'
            print u'Ничего страшного, просто прямоугольные картинки для обложки не будут обрезаться до квадратных'

    print ' MP3s:'
    for i, song in enumerate(songs):
        download(song['url'], target_dir, '%d.mp3' % (i+1), '  - ' + song['title'])

    # Parsing
    for f in os.listdir(target_dir):
        if not f.endswith('.mp3'):
            continue
        filename = os.path.join(target_dir, f)
        try:
            id3 = ID3(filename, translate=False)
        except mutagen.id3.ID3NoHeaderError:
            id3 = mutagen.id3.ID3()
        id3.unknown_frames = getattr(id3, 'unknown_frames', [])
        id3.update_to_v24()
        id3.add(TPE2(encoding=3, text=title))
        if album:
            id3.add(TAL(encoding=3, text=album))
        id3.add(TCMP(encoding=3, text='1'))
        id3.add(TRCK(encoding=3, text=''))
        if cover:
            id3.add(
                APIC(
                    encoding=3, # 3 is for utf-8
                    mime='image/jpeg', # image/jpeg or image/png
                    type=3, # 3 is for the cover image
                    desc=u'Cover',
                    data=open(cover_filename).read()
                )
            )
        id3.save(filename)
        shutil.copyfile(filename, os.path.join(itunes_autoimport_dir, f))

    os.system('rm -rf %s' % target_dir)


if __name__=='__main__':
    download_post('https://vk.com/wall-35193970_6164')