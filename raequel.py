"""RAEquel: una API para el diccionario de la Real Academia de la Lengua.
"""

__author__ = "Sebastian Oliva (yo@sebastianoliva.com)"
__version__ = "3.2"
__copyright__ = "Copyright (c) 2010-2012 Sebastian Oliva"
__license__ = "GNU AGPL 3.0"

import os
import sys

root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(root_dir, 'libs'))

import re
import json

import jinja2
import webapp2
from google.appengine.api import memcache

from rae import Drae

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


def get_lemas(word):
    lemas = memcache.get(u'{0}:lemas'.format(word))
    if lemas is not None:
        return json.loads(lemas)
    else:
        drae = Drae()
        lemas = drae.search(word)
        if not isinstance(lemas, dict):     # don't cache errors
            memcache.add(u'{0}:lemas'.format(word), json.dumps(lemas))
        return lemas


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render({}))


class JsonResults(webapp2.RequestHandler):
    def get(self):
        palabra = self.request.get('query')
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Methods'] = 'GET'
        self.response.out.write(json.dumps(get_lemas(palabra)))


class XmlResults(webapp2.RequestHandler):
    def get(self):
        palabra = self.request.get('query')
        self.response.headers['Content-Type'] = 'application/xml'
        template = jinja_environment.get_template('results.xml')

        self.response.out.write(template.render({'lemas': get_lemas(palabra)}))


app = webapp2.WSGIApplication([
    webapp2.Route('/', handler=MainPage, name='home'),
    webapp2.Route(r'/xml', handler=XmlResults, name='default_xml'),  # nopep8
    webapp2.Route(r'/json', handler=JsonResults, name='default_json'),  # nopep8
    webapp2.Route(r'/<version:v\d+>/xml', handler=XmlResults, name='xml_results'),   # nopep8
    webapp2.Route(r'/<version:v\d+>/json', handler=JsonResults, name='json_results')],  # nopep8
    debug=True)
