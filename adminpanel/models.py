from django.db import models
from django.db.models.fields import TextField

# Create your models here.
class devices(models.Model):
    email = models.EmailField(max_length=254,blank=False)
    name = models.CharField(max_length=50,blank=False,default='new device')
    status = models.BooleanField(default=False)
    note = models.TextField(max_length=200,blank=True)

class cams(models.Model):
    camname = models.CharField(max_length=50,blank=False,default='cam')
    camdevice = models.ForeignKey(devices,on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    note = models.TextField(max_length=200,blank=True)

class otp(models.Model):
    code = models.CharField(max_length=6,blank=False)
    device = models.ForeignKey(devices,on_delete=models.CASCADE)
    cam = models.ForeignKey(cams,on_delete=models.CASCADE)

