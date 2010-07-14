#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from base import BaseHandler		

class PageHandler(BaseHandler):

	def get(self, page):
		if page: 
			if(page == 'about'):
				self.render({},'about.html')
			else:
				self.error(404)
		else:
			self.error(404)
