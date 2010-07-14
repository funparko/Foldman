#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from base import BaseHandler
import app.models as models


class ImagesHandler (BaseHandler):
	def get(self, model, key):
		if key == '' or key == None:
			self.error(404)
			return
			
		if model == 'part':
			image = models.Part.get(key).full_size_image
		elif model == 'foldman':
			image = models.Foldman.get(key).full_size_image
		elif model == 'foldman_thumb':
			image = models.Foldman.get(key).thumb_image
		else:		
			self.error(404)
		
		if image:
			#i = images.resize(img.full_size_image,100,100)
			self.response.headers['Content-Type'] = "image/png"
			self.response.out.write(image)
		else:
			self.error(404)
