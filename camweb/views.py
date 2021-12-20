from django.shortcuts import render
from . import forms
from django.http import HttpResponseForbidden,HttpResponseServerError,StreamingHttpResponse,HttpResponseRedirect
from adminpanel.models import otp
import socket
import pickle
import cv2
import numpy as np
import struct
# Create your views here.
def index(request):
    if request.method == 'POST':
        form = forms.passform(request.POST)
        if form.is_valid():
            request.session['isvalid'] = True
            otpcode = form.cleaned_data['code']
            if otp.objects.filter(code=otpcode):
                data = otp.objects.get(code=otpcode)
                s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                s.connect(('127.0.0.1',5998))
                try:
                    s.send(pickle.dumps(['udpstream',data.device.id,data.cam.id]))
                    rep = pickle.loads(s.recv(1024))
                    if rep[0]:
                        request.session['port']=rep[1]
                    else:
                        return HttpResponseForbidden()
                except:
                    s.close()
                    return HttpResponseServerError()
                finally:
                    s.close()
            else:
                form = forms.passform()
                request.session['isvalid'] = False
    else:
        request.session['isvalid'] = False
        form = forms.passform()
    print(form.errors)
    return render(request,'camweb/index.html',{'forms':form,'valid':request.session['isvalid']})

# def destructure(sock):
    # while True:
    #     size = struct.calcsize('I')
    #     data = b''
    #     print('hmm')
    #     while len(data) < size:
    #         datarecv = sock.recv(2048)
    #         data+=datarecv
    #     print('recving',len(data))
    #     sizereq = data[0:size]
    #     sizereq=struct.unpack('I',sizereq)[0]
    #     data = data[size:]
    #     while len(data) < sizereq:
    #         datarecv = sock.recv(2048)
    #         data+=datarecv
    #     print('recived',len(data))
    #     data = pickle.loads(data)
        # yield(data) 
def vidmaker(request):
    if request.session['isvalid']:
        try:
            print('valid')
            port = request.session['port']
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.connect(('127.0.0.1',port))
            print('connecting to udpserv')
        except:
            request.session['isvalid'] =False
        try:
            while True:
                # data = destructure(s)
                size = struct.calcsize('I')
                data = b''
                print('hmm')
                while len(data) < size:
                    datarecv = s.recv(2048)
                    data+=datarecv
                print('recving',len(data))
                sizereq = data[0:size]
                sizereq=struct.unpack('I',sizereq)[0]
                data = data[size:]
                print(sizereq,len(data))
                while len(data) < sizereq:
                    datarecv = s.recv(sizereq-len(data))
                    data+=datarecv
                print('recived',len(data))
                data = pickle.loads(data)
                frame = data
                # frame = next(data)
                print('yielding')
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        except Exception as e:
            print(e)
            s.close()
            request.session['isvalid'] = False
            return HttpResponseRedirect('/')

def vidstream(request):
    return StreamingHttpResponse(vidmaker(request),content_type='multipart/x-mixed-replace; boundary=frame')