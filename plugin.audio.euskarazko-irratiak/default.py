# https://docs.python.org/2.7/
import os
import sys
import urllib
import urlparse
# http://mirrors.kodi.tv/docs/python-docs/
import xbmcaddon
import xbmcgui
import xbmcplugin
# http://docs.python-requests.org/en/latest/
import requests
from bs4 import BeautifulSoup

JSON_URL = 'https://raw.githubusercontent.com/aldatsa/plugin.audio.euskarazko-irratiak/master/streams/streams.json'
ARROSA_PODCASTS_URL = 'http://www.arrosasarea.eus/category/irratien-programak/'

def build_url(query):
    base_url = sys.argv[0]
    return base_url + '?' + urllib.urlencode(query)

def get_streams(url):
    """
    Get the list of audio/streams.

    :param url: str
    :return: list
    """

    data = requests.get(url)
    return data.json().get('streams')

def list_streams(streams):
    stream_list = []
    # iterate over the contents of the dictionary songs to build the list
    for stream in streams:
        # create a list item using the stream's name for the label
        li = xbmcgui.ListItem(label=stream['name'])
        # set the thumbnail image
        li.setArt({'thumb': stream['logo']})
        # set the list item to playable
        li.setProperty('IsPlayable', 'true')
        # build the plugin url for Kodi
        url = build_url({'mode': 'stream', 'url': stream['url'], 'title': stream['name']})
        # add the current list item to a list
        stream_list.append((url, li, False))
    # add list to Kodi per Martijn
    # http://forum.kodi.tv/showthread.php?tid=209948&pid=2094170#pid2094170
    xbmcplugin.addDirectoryItems(addon_handle, stream_list, len(stream_list))
    # set the content of the directory
    xbmcplugin.setContent(addon_handle, 'songs')
    xbmcplugin.endOfDirectory(addon_handle)

def play_stream(url):
    # set the path of the stream to a list item
    play_item = xbmcgui.ListItem(path=url)
    # the list item is ready to be played by Kodi
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)

def get_page(url):
    # download the source HTML for the page using requests
    # and parse the page using BeautifulSoup
    r = requests.get(url)

    if r.status_code == 404:
        return False

    return BeautifulSoup(r.text, 'html.parser')

def get_arrosa_podcasts(page):
    radios = []

    radios_li = page.select('.dcw > li')

    for radio in radios_li:
        radio_a = radio.find('a', recursive=False)
        programs = []
        for program in radio.select('ul.children li a'):
            # Remove the multiple spaces between the words
            name = ' '.join(program.string.split())
            programs.append({'name': name, 'url': program['href']})
        radios.append({'name': radio_a.string, 'programs': programs})

    return radios

def list_radios_with_podcasts(radios):
    radio_list = []
    # iterate over the contents of the list of radios to build the list
    for radio in radios:
        url = build_url({'mode': 'podcast-radio', 'foldername': radio['name']})
        li = xbmcgui.ListItem(radio['name'], iconImage='DefaultFolder.png')
        radio_list.append((url, li, False))
    # add list to Kodi per Martijn
    # http://forum.kodi.tv/showthread.php?tid=209948&pid=2094170#pid2094170
    xbmcplugin.addDirectoryItems(addon_handle, radio_list, len(radio_list))
    # set the content of the directory
    xbmcplugin.setContent(addon_handle, 'songs')
    xbmcplugin.endOfDirectory(addon_handle)

def show_main_menu():
    url = build_url({'mode': 'streams', 'foldername': 'Irratiak zuzenean'})
    li = xbmcgui.ListItem('Irratiak zuzenean', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    url = build_url({'mode': 'podcasts-radios', 'foldername': 'Podcast-ak'})
    li = xbmcgui.ListItem('Podcast-ak', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)

def main():
    args = urlparse.parse_qs(sys.argv[2][1:])
    mode = args.get('mode', None)

    # initial launch of add-on
    if mode is None:
        show_main_menu()
    # the user wants to see the list of streams
    elif mode[0] == 'streams':
        # get the JSON
        streams = get_streams(JSON_URL)
        # display the list of streams in Kodi
        list_streams(streams)
    # a stream from the list has been selected
    elif mode[0] == 'stream':
        # pass the url of the stream to play_stream
        play_stream(args['url'][0])
    # the user wants to see list of radios that have podcasts
    elif mode[0] == 'podcasts-radios':
        # parse the website of arrosa irrati sarea
        arrosa_page = get_page(ARROSA_PODCASTS_URL)
        # get the list of radios that have podcasts
        podcasts = get_arrosa_podcasts(arrosa_page)
        # display the list of radios that have podcasts
        list_radios_with_podcasts(podcasts)

if __name__ == '__main__':
    addon_handle = int(sys.argv[1])
    main()
