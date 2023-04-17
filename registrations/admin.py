from django.contrib import admin

from .models import Registration, Involved, Faq

# Register your models here.

admin.site.register(Registration)

admin.site.register(Involved)

admin.site.register(Faq)
