from base import BaseHandler
import app.models as models


class HomeHandler(BaseHandler):

	def get(self):
		template_values = {
			'finished_foldmen' : models.Foldman.all().filter('finished != ', None).order('-finished').fetch(8)
		}
		if self.current_user:
			template_values['users_foldmen'] = models.get_users_unfinished_foldmen(self.current_user)
			template_values['availble_foldmen'] = models.get_availble_foldmen(self.current_user)
			
		self.render(template_values, 'index.html')