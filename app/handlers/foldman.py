#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from base import BaseHandler
import app.models as models
import logging
		

class FoldmanHandler(BaseHandler):

	def post(self, action, key):
		foldman = models.Foldman.get(key)
		if foldman: 
			if(action == 'active'):
				models.block_foldman(foldman)
			elif(action == 'cancel'):
				models.unblock_foldman(foldman)
			elif(action == 'decline'):
				models.decline_foldman(foldman, self.current_user)
				self.redirect('/')
			else:
				self.error(404)
		else:
			self.error(404)
			
	def get(self, action, key = None):			
		if(action == 'view'):
			foldman = models.Foldman.get(key)


			if foldman and not foldman.finished == None:
				template_values = {
					'foldman': foldman,
					'parts': models.Part.all().filter('foldman = ', foldman)
				}
				
				if self.current_user:
					if self.current_user.id in foldman.not_viewed_fb_uids:
						foldman.not_viewed_fb_uids.remove(self.current_user.id) 
						foldman.put()
				
				self.render(template_values, 'foldmen_view.html')
			else:
				self.error(404)
		
		elif(action == 'cleanup'):
			models.unblock_inactive()
			# foldmen = models.Foldman.all().fetch(1000)
			# for f in foldmen:
			# 	if len(f.not_viewed_fb_uids) < 2:
			# 		f.not_viewed_fb_uids = []
			# 		f.put()
			# 
			
			# foldmen = models.Foldman.all().fetch(1000)
			# for f in foldmen:
			# 	ids = []
			# 	parts = models.Part.all().filter('foldman = ', f)
			# 	for p in parts:
			# 		if p.fb_uid and p.fb_uid not in ids:
			# 			ids.append(str(p.fb_uid))
			# 			# self.response.out.write(p.fb_uid)
			# 			# self.response.out.write("\n")
			# 		
			# 	# self.response.out.write(ids)
			# 	f.parts_fb_uids = (ids)
			# 	f.put()
			# 
			# self.response.out.write("1")


			# parts = models.Part.all().fetch(1000)
			# for part in parts:
			# 	if part.foldman.parts_finished == 1 and part.type == 'head':
			# 		part.last_finished = True
			# 	elif part.foldman.parts_finished == 2 and part.type == 'torso':
			# 		part.last_finished = True
			# 	else:
			# 		part.last_finished = False
			# 	part.put()	
				#try:
				#	foldman = part.foldman
				#except:
				#	part.delete()
				
		else:
					
			template_values = models.get_paginated_foldmen(self)
			self.render(template_values, 'foldmen_list.html')
			
			# if key:
			# 	page = int(cgi.escape(key))
			# else:
			# 	page = 1
			# count = models.Foldman.all().filter('finished !=', None).count()
			# 
			# foldmen = models.Foldman.all().filter('finished !=', None).order('-finished').fetch(PER_PAGE, PER_PAGE*(page-1))
			# template_values = {
			# 	'has_next': count > (page)*PER_PAGE,
			# 	'has_prev': page > 1,
			# 	'page': page,
			# 	'next_page': page+1,
			# 	'prev_page': page-1,
			# 	'finished_foldmen': foldmen
			# }
			# self.render(template_values, 'foldmen_list.html')
