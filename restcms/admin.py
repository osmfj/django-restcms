from django.contrib import admin

import reversion

from .models import Page, File


class PageAdmin(reversion.VersionAdmin):
    list_display = [
        'pk',
        'title',
        'language',
        'path',
        'status',
        'publish_date',
    ]


class FileAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'download_url',
        'created',
    ]


admin.site.register(Page, PageAdmin)
admin.site.register(File, FileAdmin)
