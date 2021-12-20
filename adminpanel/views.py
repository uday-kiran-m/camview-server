from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate,login,logout
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from . import forms
from . import models
# Create your views here.
@login_required(login_url= reverse_lazy('login'))
def index(request):
    devices = models.devices.objects.all()
    return render(request,'adminpanel/index.html',{'devices':devices})

@login_required(login_url= reverse_lazy('login'))
def about(request):
    return render(request,'adminpanel/about.html')

@login_required(login_url= reverse_lazy('login'))
def devices(request):
    return render(request,'adminpanel/devices.html')


def loginuser(request):
    if request.method == 'POST':
        print('hmm1')
        form = forms.loginfrom(request.POST)
        if form.is_valid():
            print('hmm')
            username = form.cleaned_data['username']
            password = form.cleaned_data['passwd']
            user = authenticate(request,username = username,password =password)
            print(username)
            if user is not None:
                login(request,user)
                return HttpResponseRedirect(reverse_lazy('index'))
            else:
                return HttpResponseRedirect('https://google.com')
    else:
        print('hmm2')
        form = forms.loginfrom()
    return render(request,'adminpanel/login.html',{'form':form})

def logoutuser(request):
    logout(request)
    return HttpResponseRedirect(reverse_lazy('login'))
