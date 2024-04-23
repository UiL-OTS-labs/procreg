from django.contrib import admin
from django.db.models import TextField

from cdh.core.forms import TinyMCEWidget

from .models import Registration, Involved, FaqList, Faq

# Register your models here.

admin.site.register(Registration)
admin.site.register(Involved)


class TinyMCEAdmin(admin.ModelAdmin):
    """
    A subcassable ModelAdmin that loads the required JS for TinyMCE.
    Admin formfields in this Admin can use the cdh.core.forms.TinyMCEWidget
    """
    class Media:
        js = (
            'cdh.core/js/jquery-3.6.1.min.js',
            'cdh.core/js/tinymce/tinymce.min.js',
            'cdh.core/js/tinymce/tinymce-jquery.min.js',
            'cdh.core/js/tinymce/shim.js',
        )


class FaqAdmin(TinyMCEAdmin):
    formfield_overrides = {
        TextField: {
            "widget": TinyMCEWidget,
        }
    }

class FaqListAdmin(TinyMCEAdmin):
    formfield_overrides = {
        TextField: {
            "widget": TinyMCEWidget,
        }
    }

admin.site.register(Faq, FaqAdmin)
admin.site.register(FaqList, FaqListAdmin)
