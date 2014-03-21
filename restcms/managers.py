from django.db import models
from django.utils import timezone


class PublishedPageManager(models.Manager):

    def get_query_set(self):
        qs = super(PublishedPageManager, self).get_query_set()
        return qs.filter(publish_date__lte=timezone.now(), status=self.model.PUBLIC)
