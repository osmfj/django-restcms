from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import static
from django.contrib.auth.decorators import login_required

from .models import Page, File
from .forms import PageForm


def can_edit(page, user):
    if page and page.is_community:
        return True
    else:
        return user.has_perm("restcms.change_page")


def get_page(path, language, published=True):
    key = {"path": path, "language": language}
    if published:
        objects = Page.published
    else:
        objects = Page.objects
    try:
        return objects.get(**key)
    except Page.DoesNotExist:
        # fallback just with path
        key = {"path": path}
        try:
            q = objects.filter(**key)
            if q.count() > 0:
                return q.all()[0]
        except Page.DoesNotExist:
            pass
        return None


def page_view(request, path):
    page = get_page(path, Page.guess_language(request.LANGUAGE_CODE))

    editable = can_edit(page, request.user)

    if page is None:
        if editable:
            return redirect("cms_page_edit", path=path)
        else:
            raise Http404

    return render(request, "cms/page_detail.html", {
        "page": page,
        "editable": editable,
    })


@login_required
def page_edit(request, path):
    language = Page.guess_language(request.LANGUAGE_CODE)
    initial = {"path": path, "language": language}
    page = get_page(published=False, **initial)

    if not can_edit(page, request.user):
        raise Http404

    if request.method == "POST":
        form = PageForm(request.POST, instance=page)
        if form.is_valid():
            page = form.save(commit=False)
            page.path = path
            page.language = language
            page.save()
            return redirect(page)
    else:
        form = PageForm(instance=page, initial=initial)

    return render(request, "cms/page_edit.html", {
        "form": form,
    })


def file_download(request, pk, *args):
    file = get_object_or_404(File, pk=pk)

    if getattr(settings, "USE_X_ACCEL_REDIRECT", False):
        response = HttpResponse()
        response["X-Accel-Redirect"] = file.file.url
        # delete content-type to allow Gondor to determine the filetype and
        # we definitely don't want Django's default :-)
        del response["content-type"]
    else:
        # enable USE_X_ACCEL_REDIRECT for production if possible.
        response = static.serve(request, file.file.name, document_root=settings.MEDIA_ROOT)

    return response
