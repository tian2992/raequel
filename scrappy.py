#basic framework imports
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
#template support
import os
from google.appengine.ext.webapp import template
#imports for the app itself
import urllib2
import json
from BeautifulSoup import BeautifulSoup

class DRAEResults(webapp.RequestHandler):
  def fetchResults(self):
    requestType = 0
    if (self.request.get('type') != None):
      requestType = self.request.get('type')
    page = urllib2.urlopen("http://buscon.rae.es/draeI/SrvltGUIBusUsual?LEMA="+self.request.get('query')+"&origen=RAE&TIPO_BUS="+requestType)
    soup = BeautifulSoup(page)
    resultList = []
    
    #for resu in soup.body.findAll("span",["eAcep", ""]):
    for resu in soup.body.findAll("span","eAcep"):
      resultList.append(resu.contents[0])
      #resu.renderContents()
    return resultList

class JSONResults(DRAEResults):
  def get(self):
    resultList = self.fetchResults()
    jsonResults = json.dumps(resultList) #results in JSON

    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(jsonResults)

class MainPage(webapp.RequestHandler):
    def get(self):
      self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
      self.response.out.write(template.render("index.html",None))
      #self.response.headers['Content-Type'] = 'text/plain'
      #self.response.out.write('Hello, World!')

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                     ('/json', JSONResults)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()