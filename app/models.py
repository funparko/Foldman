# coding=utf-8

import time
import datetime
import logging

import app.lib.facebook as facebook

from google.appengine.api import images
from google.appengine.ext import db
from google.appengine.api import mail

from app.config.config import *
from app.config.environment import *

IMAGE_PART_HEIGHT = 250;
IMAGE_FOLDING = 10;

PART_TYPES = ["head", "torso", "legs"]
NOTIFICATIONS = ["wall", "email", "none"]

class User(db.Model):
	id = db.StringProperty(required=True)
	created = db.DateTimeProperty(auto_now_add=True)
	updated = db.DateTimeProperty(auto_now=True)
	name = db.StringProperty(required=True)
	email = db.StringProperty(required=False)
	profile_url = db.StringProperty(required=True)
	access_token = db.StringProperty(required=True)
	foldman_count = db.IntegerProperty(default=0)
	default_notification = db.StringProperty(default='none',required=True, choices=set(NOTIFICATIONS))
	
	def get_url(self):
		return '/user/%s' % self.key()
	
	
class Foldman(db.Model):
	created = db.DateTimeProperty(auto_now_add=True)
	finished = db.DateTimeProperty(default=None)
	parts_finished = db.IntegerProperty(default=0,required=True, choices=set([0,1,2,3]))
	active = db.BooleanProperty(default=False)
	activated = db.DateTimeProperty(default=None)
	full_size_image = db.BlobProperty()
	thumb_image = db.BlobProperty()
	fb_uid = db.StringProperty(required=True)
	user = db.ReferenceProperty(User)
	number = db.IntegerProperty(default=None)
	
	
	@property
	def previous_part(self):
		if not hasattr(self, "_previous_part"):
			if self.parts_finished == 1:
				type = 'head'
			elif self.parts_finished == 2:
				type = 'torso'
			else:
				return None

			self._previous_part = Part.all().filter("foldman =", self).filter("type =", type).get()
		return self._previous_part

	@property
	def current_part(self):
		if not hasattr(self, "_current_part"):
			if self.parts_finished == 0:
				type = 'head'
			elif self.parts_finished == 1:
				type = 'torso'
			elif self.parts_finished == 2:
				type = 'legs'
			else:
				return None

			self._current_part = Part.all().filter("foldman =", self).filter("type =", type).get()
		return self._current_part
				

	def get_url(self):
		return '/foldman/view/%s' % self.key()
	
	def get_image_url(self):
		return "/image/foldman/%s" % self.key()

	def get_thumb_url(self):
		return "/image/foldman_thumb/%s" % self.key()


class Part(db.Model):
	foldman = db.ReferenceProperty(Foldman)
	foldman_finished = db.BooleanProperty(default=False)
	type = db.StringProperty(default="head", required=True, choices=set(PART_TYPES))
	# author = db.UserProperty()
	created = db.DateTimeProperty(auto_now_add=True)
	finished = db.DateTimeProperty(default=None)
	viewed = db.BooleanProperty(default=False)
	full_size_image = db.BlobProperty()
	fb_uid = db.StringProperty()
	user = db.ReferenceProperty(User)
	current = db.BooleanProperty(default=False)
	notification = db.StringProperty(default='none',required=True, choices=set(NOTIFICATIONS))


def get_and_block_foldman(key, user):
	foldman = Foldman.get(key)
	if foldman:
		if foldman.active == False:
			block_foldman(foldman)
			return foldman
		if foldman.current_part and foldman.current_part.fb_uid == user.id:
			block_foldman(foldman)
			return foldman
	return None
	
		
def foldman_finished(foldman):
	y = 0
	inputs = []
	users = []
	for	type in PART_TYPES:
		part = Part.gql('WHERE foldman = :foldman AND type = :type LIMIT 1', foldman=foldman.key(), type=type).get()		
		inputs.append((part.full_size_image, 0, y, 1.0, images.TOP_LEFT))		
		y = y + IMAGE_PART_HEIGHT - IMAGE_FOLDING
		
		part.foldman_finished = True
		part.put()
		
		if part.user not in users:
			users.append(part.user)
		
	foldman.full_size_image = images.composite(inputs, IMAGE_FOLDMAN_WIDTH, IMAGE_FOLDMAN_HEIGHT, 0)
	foldman.thumb_image = images.resize(foldman.full_size_image, 100, 146)
	foldman.parts_finished = len(PART_TYPES)
	foldman.finished = datetime.datetime.today()
	
	max_id_foldman = Foldman.all().order("-number").get()
	if max_id_foldman:
		foldman.number = (max_id_foldman.number+1)
	else:
		foldman.number = 1
	
	foldman.put()
	
	for	user in users:
		user.foldman_count = user.foldman_count + 1
		user.put()
		
	notify_users_finished(foldman)


def previous_part(part):
	if part.type == 'torso':
		type = 'head'
	elif part.type == 'legs':
		type = 'torso'
	else:
		return None
		
	return Part.all().filter("foldman =", part.foldman).filter("type =", type).get()
	
def get_availble_foldmen(user):
	foldmen = []
	
	parts = Part.all().filter("fb_uid =", None).filter("current =", True).filter("foldman_finished =", False).order("-created").fetch(20)
	
	for part in parts:
		if previous_part(part) and previous_part(part).user.id != user.id:
			if not part.foldman.active:
				foldmen.append(part.foldman)
	
	return foldmen
	
def set_current_part(foldman):
	if foldman.parts_finished == 1:
		type = 'torso'
	elif foldman.parts_finished == 2:
		type = 'legs'
		
	part = Part.all().filter("foldman =", foldman).filter("type =", type).get()
	part.current = True
	part.put()
	

def get_finished(fetch = 8):
	return Foldman.all().filter("parts_finished =", 3).order("-finished").fetch(fetch)
#	return Foldman.gql("WHERE finished != :finished ORDER BY finished DESC LIMIT 8", finished=None)


def unblock_inactive():
	foldmen = Foldman.gql("WHERE active = :active AND activated < :activated", 
					active=True, activated=datetime.datetime.fromtimestamp(time.time()-(60*5)))
	for foldman in foldmen:
		unblock_foldman(foldman)
	
	foldmen = Foldman.gql("WHERE parts_finished	= 0 AND created < :created", 
					created=datetime.datetime.fromtimestamp(time.time()-(60*60)))
	for foldman in foldmen:
		remove_foldman(foldman)
	
def create_foldman(user):
	foldman = Foldman(user = user, fb_uid = user.id, active = True, activated = datetime.datetime.now())
	foldman.put()
	for	type in PART_TYPES:
		part = Part(parent = foldman, type=type, foldman=foldman)
		if type == 'head':
			part.fb_uid = user.id
			part.user = user
		part.put()
	return foldman	


def get_users_unfinished_foldmen(user):
	parts = Part.all().filter("fb_uid =", user.id).filter("current =", True).order("-finished").fetch(10)
	if parts:
		foldmen = []
		for part in parts:
			foldmen.append(part.foldman)
		return foldmen

def get_users_foldmen(user, current_user):
	parts = Part.all().filter("user =", user).filter("foldman_finished =", True).order("-finished").fetch(100)
	foldmen = []
	keys = []
	for part in parts:		
		if  not part.viewed and current_user and current_user.id == user.id:
			part.foldman.unviewed = True

		if not part.foldman.key() in keys:
			foldmen.append(part.foldman)
			keys.append(part.foldman.key())
	return foldmen


		
def get_users_unviewed_foldmen(user):
	if user:
		#parts = Part.gql("WHERE author = :user AND viewed = :viewed", viewed=False, user=user)
		q = Part.all().filter("user =", user).filter("viewed =", False).filter("foldman_finished =", True)
		foldmen_keys = []
		if q.count() == 0:
			return 0
		parts = q.fetch(100)
		for part in parts:
			if part.foldman.key() not in foldmen_keys:
				foldmen_keys.append(part.foldman.key())
		return len(foldmen_keys)
			
	return Foldman.all().filter("__key__ IN", foldmen_keys).filter("finished != ", None).count()		
#	return Foldman.gql("WHERE __key__ IN :keys AND finished != :finished ORDER BY finished DESC LIMIT 100", 
#						keys=foldmen_keys, finished=None).count()		
			

def get_current_part(foldman):
	prev_part = None
	for	type in PART_TYPES:
		part = Part.all().filter("foldman =", foldman).filter("type", type).get()
		if part.finished == None:
			if type != 'head':
				part.prev_part = prev_part
			return part
		prev_part = part



def block_foldman(foldman):
	foldman.active = True
	foldman.activated = datetime.datetime.today()
	foldman.put()

def remove_foldman(foldman): 
	for	type in PART_TYPES:
		part = Part.all().filter("foldman =", foldman).filter("type", type).get()
		part.delete()
	foldman.delete()
	
def unblock_foldman(foldman):
	if foldman.parts_finished == 0:
		remove_foldman(foldman)
	else:
		foldman.active = False
		foldman.activated = None
		foldman.put()
		
def decline_foldman(foldman, user):
	if foldman.parts_finished == 0:
		remove_foldman(foldman)
	elif foldman.current_part and foldman.current_part.fb_uid == user.id:
		part = foldman.current_part
		part.fb_uid = None
		part.put()
	
def notify_users_finished(foldman):
	for	type in PART_TYPES:
		if type != 'legs':
			part = Part.all().filter("foldman =", foldman).filter("type", type).get()
			if part.notification == 'wall':
				publish_stream_finished(part.user, foldman)
			elif part.notification == 'email':
				send_email_finished(part.user, foldman)

def notify_next_user(foldman, friend_id):
	part = Part.all().filter("foldman =", foldman).filter("type", type).get()
	
	# for	type in PART_TYPES:
	# 	if type != 'legs':
	# 		part = Part.all().filter("foldman =", foldman).filter("type", type).get()
	# 		if part.notification == 'wall':
	# 			publish_stream_finished(part.user, foldman)
	# 		elif part.notification == 'email':
	# 			send_email_finished(part.user, foldman)
		
	
	
def publish_stream_friend(user, friend_id):
	attachment = {
		"name": "Vikgubbe",
		"link": URL,
		"description": "Följ länken för att rita vikgubben"
		#"picture": "http://www.example.com/thumbnail.jpg"
	}
	graph = facebook.GraphAPI(user.access_token)
	graph.put_wall_post("Fortsätt rita på en vikgubbe jag skapat", attachment, "100001076356513")
	
def publish_stream_finished(user, foldman):
	att = {
		"name": "Vikgubbe",
		"link": URL + foldman.get_url(),
		"description": "Följ länken för att se vikgubben",
		"picture": URL + foldman.get_image_url()
	}
	graph = facebook.GraphAPI(user.access_token)
	graph.put_wall_post("Din vikgubbe är klar", att, "100001076356513")
	
def send_email_finished(user, foldman):
	if mail.is_email_valid(user.email):
		url = URL + foldman.get_url()
		sender_address = "Vikgubbe <noreply@vikgubbe.appspotmail.com>"
		subject = "Din vikgubbe är klar"
		body = """
Klicka på länken nedan för att se din vikgubbe:

%s
""" % url

		mail.send_mail(sender_address, user.email, subject, body)
