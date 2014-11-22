#!/usr/bin/env python2.7
# -*- coding:utf-8 -*-
from sdk.weibo import APIClient
import urllib, os, sys
import webbrowser
import urllib2


class sina_reptile:
	def __init__(self, app_key, app_secret):
		self.APP_KEY = app_key
		self.APP_SECRET = app_secret
		self.CALLBACK_URL = 'https://api.weibo.com/oauth2/default.html'

