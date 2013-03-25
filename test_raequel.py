# -*- coding: utf-8 -*-

import json
import unittest

import webapp2

import raequel


class TestHandlers(unittest.TestCase):

    def test_index(self):
        request = webapp2.Request.blank('/')
        response = request.get_response(raequel.app)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'text/html; charset=utf-8')   # nopep8

    def test_json_default_handler(self):
        request = webapp2.Request.blank('/json?query=amor')
        response = request.get_response(raequel.app)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        for lema in json.loads(response.body):
            self.assertTrue(isinstance(lema, basestring))

    def test_xml_default_handler(self):
        request = webapp2.Request.blank('/xml?query=amor')
        response = request.get_response(raequel.app)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/xml; charset=utf-8')  # nopep8

    def test_json_v2_handler(self):
        request = webapp2.Request.blank('/v2/json?query=amor')
        response = request.get_response(raequel.app)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        for lema in json.loads(response.body):
            self.assertTrue(isinstance(lema, dict))
