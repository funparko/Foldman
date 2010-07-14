from base import BaseHandler
import app.models as models


class HomeHandler(BaseHandler):

	def get(self):
		template_values = {
			'finished_foldmen' : models.Foldman.all().filter('finished != ', None).order('-finished')
		}
		# foldmen = models.Foldman.all().order('finished').fetch(100)
		# i = 1
		# for f in foldmen:
		# 	if f.finished != None:
		# 		f.number = i
		# 		f.put()
		# 		i = i + 1
		# 	else:
		# 		f.number = None
		# 		f.put()
		# 		
		if self.current_user:
			template_values['users_foldmen'] = models.get_users_unfinished_foldmen(self.current_user)
			template_values['availble_foldmen'] = models.get_availble_foldmen(self.current_user)
			
		self.render(template_values, 'index.html')