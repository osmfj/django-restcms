import os
import re

from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.encoding import force_bytes

import reversion

from .managers import PublishedPageManager


class Page(models.Model):
    """
    >>> from django.conf import settings
    >>> lang = settings.LANGUAGES[0][0]
    >>> _ = Page.objects.create(path="path1/", content="content", language=lang)

    Page is unique under path and language.
    >>> Page.objects.create(path="path1/", content="content", language=lang)
    Traceback (most recent call last):
        ...
    ValidationError: {'__all__': [u'Page with this Path and Language already exists.']}

    So when one of them is different, its acceptable.
    >>> lang2 = settings.LANGUAGES[1][0]
    >>> _ = Page.objects.create(path="path2/", content="content", language=lang)
    >>> _ = Page.objects.create(path="path2/", content="content", language=lang2)

    The path value must not be started with "/" and be ends with "/".
    >>> Page.objects.create(path="/path", content="content", language=lang)
    Traceback (most recent call last):
        ...
    ValidationError: {'path': ...}

    The content must actually be a reStructuredText.
    >>> page = Page.objects.create(path="path3/", content="Hello\\n=====\\n\\nHow are you?\\n\\nTopics\\n------", language=lang)
    >>> print page.title
    Hello
    >>> print page.body # doctest: +NORMALIZE_WHITESPACE
    <p>How are you?</p>
    <div class="section" id="topics">
    <h1>Topics</h1>
    </div>

    The content may have subtitle because of reStructuredText.
    >>> page = Page.objects.create(path="path4/", content="Hello\\n=====\\n\\nSub title\\n---------\\n\\nHow are you?", language=lang)
    >>> print page.title
    Hello
    >>> print page.subtitle
    Sub title
    >>> print page.body # doctest: +NORMALIZE_WHITESPACE
    <p>How are you?</p>
    """

    DRAFT = 1
    PUBLIC = 2
    REJECT = 3
    STATUS_CHOICES = (
        (DRAFT, _(u"Draft")),
        (PUBLIC, _(u"Public")),
        (REJECT, _(u"Reject")),
    )

    PATH_RE = getattr(settings, 'RESTCMS_PAGE_PATH_REGEX', r"(([\w-]{1,})(/[\w-]{1,})*)/")

    path = models.CharField(max_length=100)
    content = models.TextField()
    language = models.CharField(max_length=100, choices=settings.LANGUAGES)
    status = models.IntegerField(choices=STATUS_CHOICES, default=DRAFT)
    publish_date = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    published = PublishedPageManager()

    class Meta:
        unique_together = (("path", "language"),)

    def __unicode__(self):
        return '%s(%s)' % (self.title, self.language)

    def __init__(self, *args, **kwargs):
        super(Page, self).__init__(*args, **kwargs)
        self._out = None

    @property
    def title(self):
        if self._out is None:
            self._render_content()
        return self._out.get('title')

    @property
    def subtitle(self):
        if self._out is None:
            self._render_content()
        return self._out.get('subtitle')

    @property
    def body(self):
        if self._out is None:
            self._render_content()
        return self._out.get('body')

    @property
    def html_title(self):
        if self._out is None:
            self._render_content()
        return self._out.get('html_title')

    @property
    def html_subtitle(self):
        if self._out is None:
            self._render_content()
        return self._out.get('html_subtitle')

    @property
    def html_body(self):
        if self._out is None:
            self._render_content()
        return self._out.get('html_body')

    def _render_content(self):
        try:
            from docutils.core import publish_parts
        except ImportError:
            if settings.DEBUG:
                raise IOError("The Python docutils library isn't installed.")
            self._out = {}
        else:
            docutils_settings = getattr(settings, "RESTRUCTUREDTEXT_FILTER_SETTINGS", {})
            self._out = publish_parts(source=force_bytes(self.content),
                                      writer_name="html4css1",
                                      settings_overrides=docutils_settings)

    @models.permalink
    def get_absolute_url(self):
        return ("cms_page", [self.path])

    @property
    def is_community(self):
        return self.path.lower().startswith("community/")

    def publish(self):
        self.status = Page.PUBLIC
        self.full_clean()

    def reject(self):
        self.status = Page.REJECT
        self.full_clean()

    def clean_fields(self, exclude=None):
        super(Page, self).clean_fields(exclude)
        self._render_content()
        self.validate_path()
        self.update_publish_date()

    def update_publish_date(self):
        if self.status == Page.PUBLIC:
            if self.publish_date is None:
                self.publish_date = timezone.now()
        else:
            self.publish_date = None

    def validate_path(self):
        if not re.match(Page.PATH_RE, self.path):
            raise ValidationError({"path": [_(u"Path can only contain letters, numbers and hyphens and end with /")]})

    @classmethod
    def guess_language(cls, language):
        languages = dict(settings.LANGUAGES)
        if language in languages:
            return language
        pos = language.find('-')
        if pos > 0:
            language = language[0:pos]
            if language in languages:
                return language
        return None

    def save(self, **kwargs):
        self.full_clean()
        return super(Page, self).save(**kwargs)


reversion.register(Page)


def generate_filename(instance, filename):
    return filename


class File(models.Model):

    file = models.FileField(upload_to=generate_filename)
    created = models.DateTimeField(auto_now=True)

    def download_url(self):
        return reverse("file_download", args=[self.pk, os.path.basename(self.file.name).lower()])