#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#    Copyright (C) 2017 Asier Iturralde Sarasola
#
#    This file is part of plugin.audio.euskarazko-irratiak.
#
#    plugin.audio.euskarazko-irratiak is free software: you can redistribute it
#    and/or modify it under the terms of the GNU General Public License as
#    published by the Free Software Foundation, either version 3 of the License,
#    or (at your option) any later version.
#
#    plugin.audio.euskarazko-irratiak is distributed in the hope that it will
#    be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with plugin.audio.euskarazko-irratiak.
#    If not, see <http://www.gnu.org/licenses/>.
#

# http://docs.python-requests.org/en/latest/
import requests
from datetime import datetime
import time
import HTMLParser
from bs4 import BeautifulSoup, BeautifulStoneSoup

# RSS from Gamerauntsia
GAMERAUNTSIA_RSS_URL = 'https://gamerauntsia.eus/feed/podcastak/denboraren-okarina/mp3/rss/'

radios = [{
    'name': 'Gamerauntsia',
    'url': ''
}]

def get_radios():
    return radios

def is_in_list_of_radios(name):
    for radio in radios:
        if radio['name'] == name:
            return True

    return False

def get_programs():
    program_list = []

    program_list.append({'name': 'Denboraren Okarina', 'url': GAMERAUNTSIA_RSS_URL, 'radio': 'Gamerauntsia'})

    return program_list

def get_audios(url):
    audios = []

    data = requests.get(url)
    contents = BeautifulSoup(data.text, 'lxml')
    image_url = contents.select('channel > image > url')[0].text

    audio_items = contents.select('item')

    for audio_item in audio_items:
        title = audio_item.select('> title')[0].text

        # Change the format of the date
        # TypeError: attribute of type 'NoneType' is not callable
        # http://forum.kodi.tv/showthread.php?tid=112916
        try:
            dateobj = datetime.strptime(audio_item.select('> pubdate')[0].text, "%a, %d %b %Y %H:%M:%S +0000")
        except TypeError:
            dateobj = datetime(*(time.strptime(audio_item.select('> pubdate')[0].text, "%a, %d %b %Y %H:%M:%S +0000")[6:16]))

        date = dateobj.strftime("%Y/%m/%d")

        # Parse the url of the audio
        audio_url = audio_item.select('> enclosure')[0]['url']

        audios.append({'title': title, 'date': date, 'image': image_url, 'url': audio_url})

    return audios
