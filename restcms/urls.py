from django.conf.urls import url, patterns
from .models import Page


urlpatterns = patterns("restcms.views",
    url(r"^files/(\d+)/([^/]+)$", "file_download", name="file_download"),
    url(r"^(?P<path>%s)_edit/$" % Page.PATH_RE, "page_edit", name="cms_page_edit"),
    url(r"^(?P<path>%s)$" % Page.PATH_RE, "page_view", name="cms_page"),
)
