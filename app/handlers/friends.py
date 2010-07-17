
#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from base import BaseHandler
import app.lib.facebook as facebook
import app.models as models


class FriendsHandler(BaseHandler):
	def get(self, key):
		if not self.require_login():  return
		
		graph = facebook.GraphAPI(self.current_user.access_token)
		friends = graph.get_connections(self.current_user.id, "friends")
		foldman = models.Foldman.get(key)	
		if foldman:
			template_values = {
				'friends' : friends['data'],
				'foldman' : foldman
			}
			self.render(template_values, 'choose_friends.html')
		else:
			self.error(404)
		

	def post(self, key):
	
		foldman = models.Foldman.get(key)

		if foldman:
			if self.request.get('notification') != "": 
				user = self.current_user
				user.default_notification = self.request.get('notification')
				user.put()
			
				part = models.Part.all().filter('foldman = ', foldman).filter('user = ', user).get()
				part.notification = self.request.get('notification')
				part.put()
			
			
			if self.request.get('skip') != "":
				models.unblock_foldman(foldman)
			else:
				fb_id = (self.request.get('fb_id'))
				if 	(fb_id != "" and self.current_user.id != int(self.request.get('fb_id'))):
					if foldman.parts_finished == 1:
						type = 'torso'
					elif foldman.parts_finished == 2:
						type = 'legs'
					
					part = models.Part.all().filter('foldman = ', foldman).filter('type = ', type).get()	
					part.fb_uid = fb_id
					part.put()
					
					foldman.public = False
					foldman.put()
					
					models.publish_stream_friend(self.current_user, fb_id, foldman)
				
			models.unblock_foldman(foldman)
			self.redirect('/')
		else:
			self.error(404)
		
		
		
