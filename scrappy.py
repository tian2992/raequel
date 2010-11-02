#basic framework imports
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
#template support
import os
from google.appengine.ext.webapp import template
#imports for the app itself
import urllib2
try:
    import simplejson as json
except ImportError:
    import json
from BeautifulSoup import BeautifulSoup
import re

class DRAEResults(webapp.RequestHandler):
  def fetchResults(self):
    query = ""
    #>print self.request.path
    #/json
    fetchString = re.search("/w/(json|xml)/(.*)",self.request.path)
    if (fetchString != None):
      query = fetchString.group(2) #group(1) is either XML or JSON
    else:
      query = self.request.get('query')
    requestType = 0
    if (self.request.get('type') != None):
      requestType = self.request.get('type')
    
    resultList = []
    try:
      page = urllib2.urlopen("http://buscon.rae.es/draeI/SrvltGUIBusUsual?LEMA="+query+"&origen=RAE&TIPO_BUS="+requestType)
      soup = BeautifulSoup(page)
    
      #for resu in soup.body.findAll("span",["eAcep", ""]):
      for resu in soup.body.findAll("span","eAcep"):
        resultList.append(resu.getText().encode("utf-8"))
        #resu.renderContents()
    except:
      resultList = []
      
    return resultList

class JSONResults(DRAEResults):
  def get(self):
    resultList = self.fetchResults()
    jsonResults = json.dumps(resultList) #results in JSON

    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(jsonResults)

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