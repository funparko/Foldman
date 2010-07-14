#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from base import BaseHandler


class RssHandler(BaseHandler):
	def get(self):
		template_values = {
			'foldmen': models.get_finished(20),
			'http_host': os.environ['HTTP_HOST']
		}
		self.render(template_values, 'rss.xml')