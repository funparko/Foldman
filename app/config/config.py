import os

if os.environ['SERVER_SOFTWARE'].startswith('Dev'):
	ENVIRONMENT = 'development'
	DEBUG = True
else:
	ENVIRONMENT = 'production'
	DEBUG = False
