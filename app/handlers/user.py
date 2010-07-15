#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from base import BaseHandler
from app.models import User
import app.models as models



class UserHandler(BaseHandler):

	def get(self, key):
		
		if key != '':
			user = User.get(key)
		else:
			user = self.current_user

		if user:
			template_values = models.get_paginated_foldmen(self, user, self.current_user)
			
			if self.current_user.id == user.id:
				for foldman in template_values['finished_foldmen']:
					if self.current_user.id in foldman.not_viewed_fb_uids:
						foldman.not_viewed = True

			template_values['user'] = user
			self.render(template_values, 'user.html')
		else:
			self.error(404)
		