=======
restcms
=======

Quick start
-----------

1. Add "restcms" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'restcms',
    )

2. Include the restcms URLconf in your project urls.py like this::

    url(r'^restcms/', include('restcms.urls')),

3. Run `python manage.py migrate` to create the restcms models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a poll (you'll need the Admin app enabled).

5. Visit http://127.0.0.1:8000/restcms/ to participate in the poll.
