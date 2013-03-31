# -*- coding: utf-8 -*-

# This file is part of periscope.
# Copyright (c) 2008-2011 Matias Bordese
#
#  periscope is free software; you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  periscope is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with periscope; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import logging
import urllib
from BeautifulSoup import BeautifulSoup

import SubtitleDatabase


LANGUAGES = {"es": "Spanish"}


class SubDivX(SubtitleDatabase.SubtitleDB):
    url = "http://www.subdivx.com"
    site_name = "SubDivX"

    def __init__(self, config, cache_folder_path):
        super(SubDivX, self).__init__(LANGUAGES)
        self.api_base_url = 'http://www.subdivx.com/index.php'

    def process(self, filepath, langs):
        if 'es' not in langs:
            return []

        fname = unicode(self.getFileName(filepath).lower())
        guessedData = self.guessFileData(fname)
        if guessedData['type'] == 'tvshow':
            subs = self.query(guessedData['name'],
                              guessedData['season'],
                              guessedData['episode'])
            return subs
        elif guessedData['type'] == 'movie':
            subs = self.query(guessedData['name'])
            return subs
        else:
            return []

    def _get_result_title(self, result):
        return result.find('a', {'class': 'titulo_menu_izq'}).text

    def _get_result_link(self, result):
        details = result.findNext('div', {'id': 'buscador_detalle'})
        link = details.findAll('div')[1].findAll('a')[-1].get('href')
        return link

    def query(self, name, season=None, episode=None):
        sublinks = []

        if season and episode:
            query = "%s s%02de%02d" % (name, season, episode)
        else:
            query = name

        params = {'buscar': query,
                  'accion': '5',
                  'oxdown': '1', }
        encoded_params = urllib.urlencode(params)
        query_url = '%s?%s' % (self.api_base_url, encoded_params)

        logging.debug("query: %s", query_url)

        content = self.downloadContent(query_url, timeout=3)
        if content is not None:
            soup = BeautifulSoup(content)
            for subs in soup('div', {"id": "menu_detalle_buscador"}):
                result = {}
                result["release"] = self._get_result_title(subs)
                result["lang"] = 'es'
                result["link"] = self._get_result_link(subs)
                result["page"] = query_url
                sublinks.append(result)
        return sublinks
