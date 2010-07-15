#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#	 http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# sys.path.append("libs")


#URL = 'http://rita.vikgub.be'

import wsgiref.handlers
import os
import sys
import cgi

from app.handlers.base import BaseHandler
from app.handlers.home import HomeHandler
from app.handlers.canvas import CanvasHandler
from app.handlers.foldman import FoldmanHandler
from app.handlers.rss import RssHandler
from app.handlers.friends import FriendsHandler
from app.handlers.images import ImagesHandler
from app.handlers.user import UserHandler
from app.handlers.page import PageHandler

from google.appengine.ext import webapp


def main():
	application = webapp.WSGIApplication(
	[
		('^/$', HomeHandler),
		('/canvas/(.*)', CanvasHandler),
		('/parts/save', CanvasHandler),
		('/foldman/(.*)/(.*)', FoldmanHandler),
		('/foldman/(.*)', FoldmanHandler),
		('/vikgubbe/(.*)', FoldmanHandler),		
		('/user/(.*)', UserHandler),		
		('/rss/?', RssHandler),
		('/page/(.*)', PageHandler),
		('/friends/(.*)', FriendsHandler),
	#	('/json/(.*)', JsonHandler),
		('/image/(.*)/(.*)', ImagesHandler)
#		('/part/save', PartHandler),
	], debug=True)
	wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
	main()
