=======
restcms
=======

.. image:: https://drone.io/bitbucket.org/pyconjp/django-restcms/status.png
   :target: https://drone.io/bitbucket.org/pyconjp/django-restcms

Quick start
-----------

1. Add "restcms" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'reversion',  # dependent
        'restcms',
    )

2. Include the restcms URLconf in your project urls.py like this::

    url(r'^restcms/', include('restcms.urls')),

3. Run `python manage.py migrate` to create the restcms models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a page (you'll need the Admin app enabled).

5. Visit http://127.0.0.1:8000/restcms/{{ path }}.
