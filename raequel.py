"""RAEquel: una API para el diccionario de la Real Academia de la Lengua."""

__author__ = "Sebastian Oliva (yo@sebastianoliva.com)"
__version__ = "3.5"
__copyright__ = "Copyright (c) 2010-2012 Sebastian Oliva"
__license__ = "GNU AGPL 3.0"

import os
import sys
import logging

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT_DIR, 'libs'))

if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine'):
    from google.appengine.api import memcache
    MEMCACHE = memcache
    DEBUG = False
else:
    sys.path.insert(0, os.path.join(ROOT_DIR, 'third_party'))

    try:
        import memcache
        MEMCACHE = memcache.Client(['127.0.0.1:11211'], debug=0)
    except:
        from mockcache import Client
        MEMCACHE = Client()
    #DEBUG = True

import json
from functools import wraps
from itertools import chain

import jinja2
import webapp2

from third_party.pyrae import pyrae



jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(ROOT_DIR, 'templates')))


def cache(mc):

    def decorator(func):
        @wraps(func)
        def wrapper(word):
            lemas = mc.get(u'{0}:lemas'.format(word))
            if lemas:
                return json.loads(lemas)
            lemas = func(word)
            mc.add(u'{0}:lemas'.format(word), json.dumps(lemas))
            return lemas
        return wrapper

    return decorator


@cache(MEMCACHE)
def get_lemas(word):
    return pyrae.DLE.search_word(word)


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render({}))


class JsonResults(webapp2.RequestHandler):
    def get(self, palabra = "", version='v1'):
        if palabra == "":
            palabra = self.request.get('query')
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Methods'] = 'GET'
        lemas = get_lemas(palabra)
        if version == 'v1':
            try:
                lemas = list(chain(*[lema['definiciones'] for lema in lemas]))   # nopep8
                logging.info("""Fetching results for: '{0}' in JSON Format.""".format(palabra))
            except TypeError:
                lemas = ""
                logging.debug("""Word: '{0}' not found""".format(palabra))
        self.response.out.write(json.dumps(lemas))


class XmlResults(webapp2.RequestHandler):
    def get(self, palabra = "", version='v1'):
        if palabra == "":
            palabra = self.request.get('query')
        self.response.headers['Content-Type'] = 'application/xml; charset=utf-8'  # nopep8
        lemas = get_lemas(palabra)
        tmpl_name = 'results_v2.xml'
        if version == 'v1':
            tmpl_name = 'results_v1.xml'
            try:
                lemas = list(chain(*[lema['definiciones'] for lema in get_lemas(palabra)]))   # nopep8
                logging.info("""Fetching results for: '{0}' in XML Format.""".format(palabra))
            except TypeError:
                logging.debug("""Word: '{0}' not found""".format(palabra))
                lemas = ""
        template = jinja_environment.get_template(tmpl_name)
        self.response.out.write(template.render({'lemas': lemas}))


app = webapp2.WSGIApplication([
    webapp2.Route('/', handler=MainPage, name='home'),
    webapp2.Route(r'/xml', handler=XmlResults, name='default_xml'),  # nopep8
    webapp2.Route(r'/json', handler=JsonResults, name='default_json'),  # nopep8
    webapp2.Route(r'/w/xml/<palabra>', handler=XmlResults, name='rest_xml'), # nopep8
    webapp2.Route(r'/w/json/<palabra>', handler=JsonResults, name='rest_json'), # nopep8
    webapp2.Route(r'/<version:v\d+>/xml', handler=XmlResults, name='xml_results'),   # nopep8
    webapp2.Route(r'/<version:v\d+>/json', handler=JsonResults, name='json_results')],  # nopep8
    debug=True)
