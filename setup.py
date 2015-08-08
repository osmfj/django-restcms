import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

tests_require = [
    'six==1.6.1',
]

setup(
    name='django-restcms',
    version='0.1',
    packages=['restcms'],
    include_package_data=True,
    license='BSD License',
    description='A simple Django cms with reStructuredText.',
    long_description=README,
    url='https://bitbucket.org/pyconjp/django-restcms/overview',
    author='Yusuke MURAOKA',
    author_email='yusuke@jbking.org',
    install_requires=[
        'Django==1.7.9',
        'django-reversion==1.8.7',
        'docutils==0.12',
    ],
    tests_require=tests_require,
    extras_require={'testing': tests_require},
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        #'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        # by this issue, we cannot test anyway.
        # https://github.com/pypa/pip/issues/1513
        # 'Programming Language :: Python :: 3.1',
        #'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
