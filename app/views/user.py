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
			template_values = {
				'foldmen': models.get_users_foldmen(user, self.current_user),
				'user': user
			}
			self.render(template_values, 'user.html')
		else:
			self.error(404)
		