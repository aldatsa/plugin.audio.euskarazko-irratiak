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

def play_audio(url):
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

def get_arrosa_radios_with_podcasts(page):
    radios = {}

    radios_li = page.select('.dcw > li')

    for radio in radios_li:
        radio_a = radio.find('a', recursive=False)
        name = radio_a.string
        url = radio_a['href']
        radios[name] = {'name': name, 'url': url}

    return radios

def list_radios_with_podcasts(radios):
    radio_list = []
    # iterate over the contents of the list of radios to build the list
    for key, value in sorted(radios.items()):
        url = build_url({'mode': 'podcasts-radio', 'foldername': value['name'], 'url': value['url']})
        li = xbmcgui.ListItem(value['name'], iconImage='DefaultFolder.png')
        radio_list.append((url, li, True))
    # add list to Kodi per Martijn
    # http://forum.kodi.tv/showthread.php?tid=209948&pid=2094170#pid2094170
    xbmcplugin.addDirectoryItems(addon_handle, radio_list, len(radio_list))
    # set the content of the directory
    xbmcplugin.setContent(addon_handle, 'songs')
    xbmcplugin.endOfDirectory(addon_handle)

def get_arrosa_programs(page):
    programs = {}

    programs_li = page.select('.dcw > li')

    for program in programs_li:
        program_a = program.find('a', recursive=False)
        name = program_a.string
        url = program_a['href']
        programs[name] = {'name': name, 'url': url}

    return programs

def list_programs(programs):
    program_list = []
    # iterate over the contents of the list of programs to build the list
    for key, value in sorted(programs.items()):
        url = build_url({'mode': 'podcasts-radio-program', 'foldername': value['name'], 'url': value['url']})
        li = xbmcgui.ListItem(value['name'], iconImage='DefaultFolder.png')
        program_list.append((url, li, True))

    # add list to Kodi per Martijn
    # http://forum.kodi.tv/showthread.php?tid=209948&pid=2094170#pid2094170
    xbmcplugin.addDirectoryItems(addon_handle, program_list, len(program_list))
    # set the content of the directory
    xbmcplugin.setContent(addon_handle, 'songs')
    xbmcplugin.endOfDirectory(addon_handle)

def get_arrosa_audios_from_page(page):
    audios = []
    audios_div = page.select('.post')

    for audio in audios_div:
        title = audio.select('.big-title h3 a')[0].text
        date = audio.select('.magz-meta')[0].text.split('|')[0].strip()
        image = audio.select('.magz-image img')[0]['src']
        url = ''
        if len(audio.select('.powerpress_link_d')) > 0:
            url = audio.select('.powerpress_link_d')[0]['href']
        audios.append({'title': title, 'date': date, 'image': image, 'url': url})

    return audios

def get_arrosa_audios(base_url):
    index = 1
    audios = []

    while True:
        podcast_page = get_page(base_url + 'page/' + str(index))

        if podcast_page:
            audios = audios + get_arrosa_audios_from_page(podcast_page)
            index = index + 1
        else:
            break

    return audios

def list_podcast_audios(audios):
    audio_list = []
    # iterate over the audios to build the list
    for audio in audios:
        # create a list item using the audio's title for the label
        li = xbmcgui.ListItem(audio['date'] + " - " + audio['title'])
        # set the thumbnail image
        li.setArt({'thumb': audio['image']})
        # set the list item to playable
        li.setProperty('IsPlayable', 'true')
        # build the plugin url for Kodi
        url = build_url({'mode': 'stream', 'url': audio['url'], 'title': audio['date'] + " - " + urllib.quote(audio['title'].encode('utf8'))})
        # add the current list item to a list
        audio_list.append((url, li, False))
    # add list to Kodi per Martijn
    # http://forum.kodi.tv/showthread.php?tid=209948&pid=2094170#pid2094170
    xbmcplugin.addDirectoryItems(addon_handle, audio_list, len(audio_list))
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
        # pass the url of the stream to play_audio
        play_audio(args['url'][0])
    # the user wants to see the list of radios that have podcasts
    elif mode[0] == 'podcasts-radios':
        # parse the website of arrosa irrati sarea
        arrosa_page = get_page(ARROSA_PODCASTS_URL)
        # get the list of radios that have podcasts
        podcasts = get_arrosa_radios_with_podcasts(arrosa_page)
        # display the list of radios that have podcasts
        list_radios_with_podcasts(podcasts)
    # the user wants to see the list of programs of a radio
    elif mode[0] == 'podcasts-radio':
        # parse the website of the podcast of the selected radio
        radio_page = get_page(args['url'][0])
        #get the list of programs of the selected radio
        programs = get_arrosa_programs(radio_page)
        # display the list of programs of the selected radio
        list_programs(programs)
    # the user wants to see the list of audios of a program
    elif mode[0] == 'podcasts-radio-program':
        # get the audios of the selected program
        audios = get_arrosa_audios(args['url'][0])
        # display the list of audios of the selected program
        list_podcast_audios(audios)
    # the user selected an audio from the list
    elif mode[0] == 'stream':
        # pass the url of the stream to play_audio
        play_audio(args['url'][0])
if __name__ == '__main__':
    addon_handle = int(sys.argv[1])
    main()
