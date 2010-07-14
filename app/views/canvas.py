#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from base import BaseHandler
import app.models as models
from google.appengine.ext import db

import base64
import datetime
import logging

class CanvasHandler(BaseHandler):

	def get(self, key):
		# foldman = models.Foldman.get(key)
		
		if key == 'new':
			foldman = models.create_foldman(self.current_user)
		else:
			foldman = models.Foldman.get(key)
			if foldman:
				if foldman.active == False:
					models.block_foldman(foldman)
				if foldman.current_part and foldman.current_part.fb_uid == self.current_user.id:
					models.block_foldman(foldman)
		
		if foldman and foldman.finished != None:
			self.redirect(foldman.get_url())
			return

		
		if foldman and (foldman.previous_part == None or foldman.previous_part.user.id != self.current_user.id):
			part = models.get_current_part(foldman)
			if part and part.finished == None:
				template_values = {
					'foldman': foldman,
					'part': part
				}
				self.render(template_values,'canvas.html')
			else:
				self.response.set_status(404, 'Not Found')
		else:
			self.response.set_status(404, 'Not Found')
			self.render({},'404.html')

	def post(self):
		part = models.Part.get(self.request.get('part_id'))
		if (part != None and part.finished == None):
			foldman = part.foldman
			
			if self.request.get('cancel') != '':
				models.unblock_foldman(foldman)
				self.redirect('/')
				return
			
			
			part.finished = datetime.datetime.today()
			part.user = self.current_user
			part.fb_uid = self.current_user.id
			
			if self.request.get('u') == '':
				self.redirect('/')
				return
				
			image = self.request.get('u').replace(' ', '+')
			image = image[image.find(',') : len(image)]
			part.full_size_image = base64.b64decode(image)
			part.last_finished = True
			part.current = False
			part.put()
			
			if part.type == "legs":
				models.foldman_finished(foldman)
				#models.publish_stream_friend(foldman.user, foldman.user.id)
				
				self.redirect(foldman.get_url())
				return
			else:
				if part.type == 'head':
					foldman.parts_finished = 1
				else:
					foldman.parts_finished = 2
				foldman.put()
				models.set_current_part(foldman)
				if part.type == 'head' or  part.type == 'torso' :
					self.redirect('/friends/' + str(foldman.key()))
				else:
					self.redirect('/')
				return
				
		else:
			self.response.set_status(404, 'Not Found')
			return	
