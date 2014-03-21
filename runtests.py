import sys
from django.conf import settings

settings.configure(DEBUG=True,
                   DATABASES={
                       'default': {
                           'ENGINE': 'django.db.backends.sqlite3',
                       }
                   },
                   ROOT_URLCONF='restcms.urls',
                   INSTALLED_APPS=('django.contrib.auth',
                                   'django.contrib.contenttypes',
                                   'django.contrib.sessions',
                                   'django.contrib.admin',
                                   'restcms',),
                   MIDDLEWARE_CLASSES=[
                       'django.contrib.sessions.middleware.SessionMiddleware',
                       'django.contrib.auth.middleware.AuthenticationMiddleware',
                       'django.middleware.locale.LocaleMiddleware',
                   ]
                   )

from django.test.simple import DjangoTestSuiteRunner
test_runner = DjangoTestSuiteRunner(verbosity=1)
failures = test_runner.run_tests(['restcms', ])
if failures:
    sys.exit(failures)