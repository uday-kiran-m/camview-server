from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.cams)
admin.site.register(models.devices)
admin.site.register(models.otp)