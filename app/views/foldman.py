#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from base import BaseHandler
import app.models as models
import logging
		
PAGESIZE = 24
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
					parts = models.Part.all().filter('foldman = ', foldman).filter('user = ', self.current_user)
					if parts:
						for part in parts:
							part.viewed = True
							part.put()
				
				self.render(template_values, 'foldmen_view.html')
			else:
				self.error(404)
		elif(action == 'cleanup'):
			models.unblock_inactive()
		else:
			next = None
			previous = None
			after = self.request.get("after")
			before = self.request.get("before")
			
			query = models.Foldman.all().filter('number !=', None)
			if after or before:						
				if after:
					foldmen = query.filter('number <=', int(after)).order("-number").fetch(PAGESIZE+1)
				elif before:
					foldmen = query.filter('number >=', int(before)).order("number").fetch(PAGESIZE+1)
					foldmen.reverse()
				
				max_number_foldman = models.Foldman.all().order("-number").get()
				if max_number_foldman and max_number_foldman.number != foldmen[0].number:
					previous = True
			
			else:
				foldmen = query.order("-number").fetch(PAGESIZE+1)

			if len(foldmen) == PAGESIZE+1:
				next = foldmen[-1].number
				foldmen = foldmen[:PAGESIZE]
					
			template_values = {
				'next': next,
				'previous': previous,
				'before': before,
				'paginate': True,
				'finished_foldmen': foldmen
			}
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
