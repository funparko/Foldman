#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import datetime
import cgi
import logging
import os
import urlparse

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext import db

import models
import wsgiref.handlers

PER_PAGE=10
class MainHandler(webapp.RequestHandler):
	def get(self, action=None, key=None):
		if key:
			page = int(key)
		else:
			page = 1
		count = models.Foldman.all().filter('finished !=', None).count()
		
		foldmen = models.Foldman.all().filter('finished !=', None).order('-finished').fetch(PER_PAGE, PER_PAGE*(page-1))
		logging.error(str(count))
		logging.error(str((page)*PER_PAGE))
		template_values = {
			'has_next': count > (page)*PER_PAGE,
			'has_prev': page > 1,
			'page': page,
			'next_page': page+1,
			'prev_page': page-1,
			'foldmen': foldmen
		}
		path = os.path.join(os.path.dirname(__file__), 'views/admin.html')
		self.response.out.write(template.render(path, template_values))

	def post(self, action=None, key=None):
		if action == 'delete':
			foldman = models.Foldman.get(key)
			foldman.delete()
		self.redirect("/home")	


def main():
	application = webapp.WSGIApplication(
	[
		('^/admin/', MainHandler),
		('^/admin/(.*)/(.*)', MainHandler),
	], debug=True)
	wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
	main()
