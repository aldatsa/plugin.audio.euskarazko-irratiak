#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#    Copyright (C) 2016 Asier Iturralde Sarasola
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

# Unofficial API for EITB Nahieran. Developed by Mikel Larreategi. Thank you very much!
# https://github.com/erral/eitbapi
EITB_NAHIERAN_API_URL = 'http://still-castle-99749.herokuapp.com/radio'

def get_programs(radio=None):
    programs_dict = {}
    data = requests.get(EITB_NAHIERAN_API_URL)
    programs = data.json().get('member')

    # Filter by radio if necessary (the radio parameter is optional)
    if radio is not None:
        programs = [program for program in programs if program['radio'] == radio]

    for program in programs:
        name = program['title']
        url = program['@id']
        radio = program['radio']
        programs_dict[name] = {'name': name, 'url': url, 'radio': radio}

    return programs_dict

def get_audios(url):
    data = requests.get(url)
    audios = data.json().get('member')

    return audios
