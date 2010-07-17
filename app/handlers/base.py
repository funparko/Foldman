from app.config.environment import *
from app.config.config import *

import app.lib.facebook as facebook
from app.lib.facebook import GraphAPIError
from google.appengine.ext import webapp
from app.models import User
import app.models as models

import os
import logging

from google.appengine.ext.webapp import template



class BaseHandler(webapp.RequestHandler):
	"""Provides access to the active Facebook user in self.current_user

	The property is lazy-loaded on first access, using the cookie saved
	by the Facebook JavaScript SDK to determine the user ID of the active
	user. See http://developers.facebook.com/docs/authentication/ for
	more information.
	"""
	@property
	def current_user(self):
		if not hasattr(self, "_current_user"):
			self._current_user = None
			cookie = facebook.get_user_from_cookie(self.request.cookies, FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)
			if cookie:
				# Store a local instance of the user data so we don't need
				# a round-trip to Facebook on every request
				user = User.get_by_key_name(cookie["uid"])
				if not user:
					graph = facebook.GraphAPI(cookie["access_token"])
					profile = graph.get_object("me")
					user = models.User(key_name=str(profile["id"]),
							id=str(profile["id"]),
							name=profile["name"],
							profile_url=profile["link"],
							email= profile["email"] if "email" in profile else None,
							access_token=cookie["access_token"])
					user.put()
				elif user.access_token != cookie["access_token"]:
					user.access_token = cookie["access_token"]
					user.put()
				
				self._current_user = user
		return self._current_user
		
	def render(self, template_values, file):
		template_values['FACEBOOK_APP_ID'] = FACEBOOK_APP_ID
		template_values['DEBUG'] = DEBUG
		template_values['URL'] = URL
		template_values['IMAGE_FOLDMAN'] = {
			'full_width' : IMAGE_FOLDMAN_WIDTH,
			'full_height' : IMAGE_FOLDMAN_HEIGHT,
			'thumb_width' : IMAGE_FOLDMAN_THUMB_WIDTH,
			'thumb_height' : IMAGE_FOLDMAN_THUMB_HEIGHT
		}
		
		template_values['finished'] = models.get_finished(10)
		template_values['current_user'] = self.current_user
		
		if self.current_user:
			template_values['unviewed_foldmen'] = models.get_users_unviewed_foldmen(self.current_user)
			
		
		path = os.path.join(os.path.dirname(__file__), '../templates/' + file)
		template_path = os.path.join(os.path.dirname(__file__), '../templates/')
		self.response.out.write(template.render(path, template_values))
	
	def is_ajax(self): 
		if not self.request.get("ajax") == '':
			return True
		return False
		
	def require_login(self): 
		if self.current_user == None:
			self.redirect('/')
			return False
		return True