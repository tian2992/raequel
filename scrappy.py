#basic framework imports
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
#template support
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
#imports for the app itself
import urllib2
try:
    import simplejson as json
except ImportError:
    import json
from BeautifulSoup import BeautifulSoup
import re


class DRAEResults(webapp.RequestHandler):
  def fetch_query(self):
    query = ""
    fetchString = re.search("/w/(json|xml)/(.*)",self.request.path)
    if (fetchString != None):
      query = fetchString.group(2) #group(1) is either XML or JSON
    else:
      query = self.request.get('query')

    return query

  def fetchResults(self):
    query = self.fetch_query()
    requestType = 0
    if (self.request.get('type') != None):
      requestType = self.request.get('type')

    resultList = []
    try:
      #page = urllib2.urlopen("http://buscon.rae.es/draeI/SrvltGUIBusUsual?LEMA="+query+"&origen=RAE&TIPO_BUS="+
      page = urllib2.urlopen("http://lema.rae.es/drae/srv/search?type="+query+"&val="+query+"&val_aux=&origen=RAE")
      soup = BeautifulSoup(page)

      #for resu in soup.body.findAll("span",["eAcep", ""]):
      for resu in soup.findAll("span","b"):
        resultList.append(resu.getText().encode("utf-8"))
        #resu.renderContents()
    except:
      resultList = []

    return resultList

class JSONResults(DRAEResults):
  def get(self):
    query = self.fetch_query()
    json_results = memcache.get(query)
    if not json_results:
        resultList = self.fetchResults()
        if resultList:
            memcache.add(query, json_results)
        json_results = json.dumps(resultList) #results in JSON

    self.response.headers['Content-Type'] = 'application/json'
    self.response.headers['Access-Control-Allow-Origin'] = '*'
    self.response.headers['Access-Control-Allow-Methods'] = 'GET'
    self.response.out.write(json_results)

class XMLResults(DRAEResults):
  def get(self):
    resultList = self.fetchResults()

    #<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    #<definitions>
    #  <definition>asdf</definition>
    #  <definition>asdf</definition>
    # </definition>

    self.response.headers['Content-Type'] = 'text/xml'

    self.response.out.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
    self.response.out.write('<definitions>\n')
    for define in resultList:
      self.response.out.write('  <definition>'+define+'</definition>\n')

    self.response.out.write('</definitions>\n')


class MainPage(webapp.RequestHandler):
    def get(self):
      self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
      self.response.out.write(template.render("index.html",None))
      #self.response.headers['Content-Type'] = 'text/plain'
      #self.response.out.write('Hello, World!')

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                     ('/json', JSONResults),
                                     ('/xml' , XMLResults ),
                                     ('/w/json/.*',JSONResults),
                                     ('/w/xml/.*',XMLResults)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

