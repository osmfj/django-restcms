from django import forms

from .models import Page


class PageForm(forms.ModelForm):

    class Meta:
        model = Page
        fields = ["content", "language", "path"]
        widgets = {
            "language": forms.HiddenInput(),
            "path": forms.HiddenInput(),
        }
