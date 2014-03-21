import tempfile

from django.core.urlresolvers import reverse
from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings

from .models import Page, File


class PageEditorRoleMixin(object):
    def loginAsPageEditor(self):
        from django.contrib.auth.models import User, Permission

        username = "user1"
        password = "passwd"
        user = User.objects.create_user(username, "foo@bar.com", password)
        permission = Permission.objects.get_by_natural_key("change_page", "restcms", "page")
        user.user_permissions.add(permission)

        assert self.client.login(username=username, password=password)


class PageMixin(object):
    def create_page(self, content="content1", path="path/",
                    language=settings.LANGUAGES[0][0], status=Page.DRAFT):
        page = Page(content=content, path=path, language=language, status=status)
        page.full_clean()
        page.save()
        return page


class PageViewTest(TestCase, PageMixin, PageEditorRoleMixin):
    def assertPageUsed(self, response, page):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]["page"], page)

    def failIfPageEditable(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context[-1]["editable"])

    def assertPageEditable(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context[-1]["editable"])

    def test_it(self):
        path = "foo/"
        url = reverse("cms_page", kwargs={"path": path})

        # no page.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        # not published yet.
        page = self.create_page(path=path, status=Page.DRAFT)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        # render page when exists and published.
        page.publish()
        page.save()
        response = self.client.get(url)
        self.assertPageUsed(response, page)
        self.assertTemplateUsed("cms/page_detail.html")

        # rejected page can not be showed anymore.
        page.reject()
        page.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_prefer_language(self):
        from django.conf import settings

        path = "foo/"
        url = reverse("cms_page", kwargs={"path": path})
        lang = settings.LANGUAGES[0][0]

        page_default = self.create_page(path=path, language=lang, status=Page.PUBLIC)

        # no language specified, uses default.
        response = self.client.get(url)
        self.assertPageUsed(response, page_default)

        # language specified but no page for the language, uses default.
        self.client.cookies[settings.LANGUAGE_COOKIE_NAME] = "ja"
        response = self.client.get(url)
        self.assertPageUsed(response, page_default)

        # language specified and the page for the language exits, uses one.
        page_ja = self.create_page(path=path, language="ja", status=Page.DRAFT)
        response = self.client.get(url)
        self.assertPageUsed(response, page_default)

        # once specified language page is published, shows it.
        page_ja.publish()
        page_ja.save()
        response = self.client.get(url)
        self.assertPageUsed(response, page_ja)

        # after specified language page rejected, it fallback to default.
        page_ja.reject()
        page_ja.save()
        response = self.client.get(url)
        self.assertPageUsed(response, page_default)

    def test_editable(self):
        path = "foo/"
        url = reverse("cms_page", kwargs={"path": path})

        page = self.create_page(path=path, status=Page.PUBLIC)

        response = self.client.get(url)
        self.assertPageUsed(response, page)
        self.failIfPageEditable(response)

        self.loginAsPageEditor()
        response = self.client.get(url)
        self.assertPageUsed(response, page)
        self.assertPageEditable(response)

    def test_editable_for_not_found(self):
        """
        If logged-in user is editor but no page exists, redirect to create page on the path.
        """
        path = "not_found/"
        view_url = reverse("cms_page", kwargs={"path": path})
        edit_url = reverse("cms_page_edit", kwargs={"path": path})

        self.loginAsPageEditor()
        response = self.client.get(view_url)
        self.assertRedirects(response, edit_url)

    def test_render_rest(self):
        path = "foo/"
        url = reverse("cms_page", kwargs={"path": path})
        page = self.create_page(path=path, content="""
Hello
=====

This is a dummy.

Sub section
-----------

Yeah.""", status=Page.PUBLIC)
        response = self.client.get(url)
        self.assertPageUsed(response, page)
        self.assertContains(response, ('<p>This is a dummy.</p>\n'
                                       '<div class="section" id="sub-section">\n'
                                       '<h1>Sub section</h1>\n<p>Yeah.</p>\n'
                                       '</div>\n'))


class PageEditTest(TestCase, PageMixin, PageEditorRoleMixin):
    def test_it(self):
        path = "foo/"
        url = reverse("cms_page_edit", kwargs={"path": path})

        # anonymous, redirect to login.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(settings.LOGIN_URL, response['Location'])

        self.loginAsPageEditor()

        # no page.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cms/page_edit.html")

        # page exists, shows edit page even draft.
        page = self.create_page(content="content_foo", path=path, status=Page.DRAFT)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cms/page_edit.html")
        self.assertContains(response, 'content_foo')

        # also it could be for rejected.
        page.reject()
        page.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cms/page_edit.html")
        self.assertContains(response, 'content_foo')

    def test_edit(self):
        path = "foo/"
        language = settings.LANGUAGES[0][0]
        view_url = reverse("cms_page", kwargs={"path": path})
        edit_url = reverse("cms_page_edit", kwargs={"path": path})

        self.loginAsPageEditor()

        # visit for creation.
        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cms/page_edit.html")

        response = self.client.post(edit_url, data={
            "content": "content1",
            "path": path,
            "language": language,
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn(view_url, response['Location'])

        # once the page is published, can be showed to others.
        page = Page.objects.get(path=path)
        page.publish()
        page.save()
        response = self.client.get(view_url)
        self.assertContains(response, "content1")
        self.assertTemplateUsed(response, "cms/page_detail.html")


class FileMixin(object):
    def create_file(self, file, name=None):
        from django.core.files import File as DjangoFile

        return File.objects.create(file=DjangoFile(file, name=name))


temp_MEDIA_ROOT = tempfile.mkdtemp()


class FileDownloadTest(TestCase, FileMixin):
    @classmethod
    def tearDownClass(cls):
        import shutil

        shutil.rmtree(temp_MEDIA_ROOT)

    @override_settings(MEDIA_ROOT=temp_MEDIA_ROOT)
    def test_it(self):
        from StringIO import StringIO

        f = self.create_file(StringIO("Hello"), "hello.txt")

        url = reverse("file_download", args=(f.pk, f.file.name))
        response = self.client.get(url)
        self.assertContains(response, "Hello")

    @override_settings(MEDIA_ROOT=temp_MEDIA_ROOT)
    def test_x_accel_redirect(self):
        from StringIO import StringIO

        f = self.create_file(StringIO("Hello"), "hello.txt")

        url = reverse("file_download", args=(f.pk, f.file.name))
        with self.settings(USE_X_ACCEL_REDIRECT=True):
            response = self.client.get(url)
        self.assertEqual(response["X-Accel-Redirect"], f.file.url)
