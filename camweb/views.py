from django.http.response import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from . import forms
from django.http import HttpResponseForbidden,HttpResponseServerError,StreamingHttpResponse,HttpResponseRedirect,Http404
from adminpanel.models import otp
import socket
import pickle
import cv2
import numpy as np
import struct
# Create your views here.
def index(request):
    if request.method == 'POST':
        print(request.POST)
        form = forms.passform(request.POST)
        if form.is_valid():
            request.session['isvalid'] = True
            otpcode = form.cleaned_data['code']
            if otp.objects.filter(code=otpcode):
                data = otp.objects.get(code=otpcode)
                if data.cam.status and data.device.status:
                    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    try:
                        s.connect(('127.0.0.1',5998))
                        s.send(pickle.dumps(['udpstream',data.device.id,data.cam.id]))
                        rep = pickle.loads(s.recv(1024))
                        print(rep)
                        if rep[0]:
                            request.session['port']=rep[1]
                            request.session['errors'] = None
                        else:
                            request.session['errors'] = 'nf'
                    except:
                        s.close()
                        request.session['errors'] = 'of'
                    finally:
                        s.close()
                else:
                    request.session['errors'] = 'of'
            else:
                form = forms.passform()
                request.session['errors'] = 'nf'
                request.session['isvalid'] = True
    else:
        request.session['isvalid'] = False
        form = forms.passform()
    print(form.errors)
    mode = request.COOKIES.get('mode')
    if mode == None:
        mode = '1'
        # request.set_cookie('mode',mode)
        request.COOKIES['mode'] = mode
    modes = ['l','d']
    return render(request,'camweb/index.html',{'forms':form,'valid':request.session['isvalid'],'mode':modes[int(mode)]})


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
                # print(request.status_code)
                # data = destructure(s)
                size = struct.calcsize('I')
                data = b''
                while len(data) < size:
                    datarecv = s.recv(2048)
                    data+=datarecv
                # print('recving',len(data))
                sizereq = data[0:size]
                sizereq=struct.unpack('I',sizereq)[0]
                data = data[size:]
                # print(sizereq,len(data))
                while len(data) < sizereq:
                    datarecv = s.recv(sizereq-len(data))
                    data+=datarecv
                # print('recived',len(data))
                data = pickle.loads(data)
                if data != None:
                    frame = data
                    # print(type(frame))
                    # print('yielding')
                    yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
                else:
                    print('hmm')
                    # frame = cv2.imread('/home/uday/server/camweb/notfound.png')
                    # frame = cv2.imencode('.jpg',frame)[1]
                    # frame = frame.tostring()
                    frame = img('notfound.png')
                    yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
                    return (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
                    break
                    
        except Exception as e:
            print(e)
            s.close()
            request.session['isvalid'] = False
            return HttpResponseRedirect('/')

def vidstream(request):
    if request.session['errors'] == None:
        return StreamingHttpResponse(vidmaker(request),content_type='multipart/x-mixed-replace; boundary=frame')
    if request.session['errors'] == 'of':
        return HttpResponse(img('offline.jpg'),content_type="image/jpeg")
    if request.session['errors'] == 'nf':
        return HttpResponse(img('nf.jpg'),content_type="image/jpeg")

def img(img):
    return open(f'/home/uday/server/camweb/img/{img}','rb').read()