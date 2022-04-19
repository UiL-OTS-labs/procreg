from django.contrib import admin
from django.contrib.auth import get_user_model

AUTH_USER_MODEL = get_user_model()

# Register your models here.


admin.site.register(AUTH_USER_MODEL)
