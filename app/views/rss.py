#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from base import BaseHandler
import app.models as models

import os

class RssHandler(BaseHandler):
	def get(self):
		template_values = {
			'foldmen': models.get_finished(20),
		}
		self.render(template_values, 'rss.xml')