import os

if os.environ['SERVER_SOFTWARE'].startswith('Dev'):
	ENVIRONMENT = 'development'
	DEBUG = True
else:
	ENVIRONMENT = 'production'
	DEBUG = False


IMAGE_FOLDMAN_WIDTH = 500;
IMAGE_FOLDMAN_HEIGHT = 730;

IMAGE_FOLDMAN_THUMB_WIDTH = 100;
IMAGE_FOLDMAN_THUMB_HEIGHT = 146;

PAGESIZE = 8