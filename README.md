Raequel
=========================================================
An API for the Real Academia Española Dictionary
------------------------------------------------

Raequel is an informal API to realize automated queries to buscon.rae.es, returning it on JSON (and then XML)
Raequel is free software under the GNU AGPL 3.0.

Dictionary Icon from http://www.openclipart.org/detail/29190

Installing
----------

Register your application in [Google App Engine](http://appengine.google.com)

upload the application using the google_app engine for python SDK

<pre>
$ cd raequel
</pre>

Modify app.yml to point to your new app engine application, you will have to modify the application name

<pre>
$ appcfg.py update .
</pre>

Using the API
-------------

GET
--------

<pre>
$ curl "http://raequel.sebastianoliva.com/json?query=idioma"
</pre>

REST
----

<pre>
$ curl "http://raequel.sebastianoliva.com/w/xml/papa"
$ curl "http://raequel.sebastianoliva.com/w/json/papa"
</pre>

JSONP
-----

You could also call it from your javascript code executed in client side.

For example, using jquery:

<pre>
<script src="jquery.js" type="text/javascript"></script>
<script type="text/javascript" charset="utf-8">
   $(function() {
    $.getJSON('http://raequel.sebastianoliva.com/w/json/idioma', function(data) {
            console.log(data);
        });
    });
</script>
</pre>

More info at [raequel.sebastianoliva.com](http://raequel.sebastianoliva.com)
