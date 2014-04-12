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
    license='BSD License',  # example license
    description='A simple Django cms with reStructuredText.',
    long_description=README,
    url='http://www.example.com/',
    author='Your Name',
    author_email='yourname@example.com',
    install_requires=[
        'Django==1.5.4',
        'django-reversion==1.7',
        'docutils==0.11',
    ],
    tests_require=tests_require,
    extras_require={'testing': tests_require},
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
