import socket
import struct
import pickle
import threading
import queue
import sys
from django.conf import settings
import django
import os

sys.path.insert(1,'../')
os.environ['DJANGO_SETTINGS_MODULE'] = 'camview.settings'
django.setup()
from adminpanel.models import devices,cams



class server:
    def __init__(self,ip,port) -> None:
        '''
        ip -> ip of this system which behaves as a server\n
        port ->port for server to accept connections

        '''
        self.ip = ip
        self.port=port
        self.status = True
        self.clients = dict()
        self.recvsize = struct.calcsize('I')
        self.portsavail = list(range(6000,6501))
        self.portsused = []
        self.frames = dict()
        self.udps = dict()
    
    def start(self):#use
        server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.ip,self.port))
        server.listen()
        client = ''
        while self.status:
            try:
                data = b''
                server.settimeout(5)
                client,addr=server.accept()
                print(addr)
            except:
                pass
            server.settimeout(None)
            if client != '':
                try:
                    while len(data) < self.recvsize:
                        data += client.recv(1024)
                    # print('recving123')
                    sizereq = data[0:self.recvsize]
                    data = data[self.recvsize:]
                    sizereq = struct.unpack('I',sizereq)[0]
                    while len(data) < sizereq:
                        data+= client.recv(1024)
                    print('recived')
                    data = pickle.loads(data)
                    if data['auth'] == 'namex':
                        # print('h')
                        if devices.objects.filter(id =data['d_id']):
                            # print('hm')
                            c_id_list = data['cams']
                            device = devices.objects.get(id = data['d_id'])
                            device.status = True
                            device.save()
                            # print('hmm')
                            for c_id in c_id_list:
                                if cams.objects.filter(id = c_id):
                                    cam = cams.objects.get(id = c_id)
                                    cam.status = True
                                    cam.save()
                                    self.frames[c_id]=queue.Queue(maxsize=100)
                                    # print('hmmm')
                            client.send('granted'.encode())
                            self.clients[data['d_id']]=[client,c_id_list]
                            client = ''
                            print('....')
                        else:
                            client.close()
                            client = ''
                    else:
                        client.close()
                        client = ''
                except KeyboardInterrupt:
                    self.status = False
                    client = ''
                    server.close()
                    print('serverclosed')
                except:
                    pass
        else:
            server.close()
            print('server close')
    def installer(self):
        instserv = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        instserv.bind((self.ip,5997))
        instserv.listen()
        client = ''
        while self.status:
            try:
                data = b''
                instserv.settimeout(5)
                client,addr=instserv.accept()
                print(addr)
            except:
                pass
            instserv.settimeout(None)
            if client != '':
                try:
                    while len(data) < self.recvsize:
                        data += client.recv(1024)
                    print('recving')
                    sizereq = data[0:self.recvsize]
                    data = data[self.recvsize:]
                    sizereq = struct.unpack('I',sizereq)[0]
                    while len(data) < sizereq:
                        data+= client.recv(1024)
                    print('recived')
                    data = pickle.loads(data)
                    if data['auth'] == 'install':
                        pass
                    if data['auth'] == 'add':
                        pass
                except KeyboardInterrupt:
                    self.status = False
                    client = ''
                    instserv.close()
                    print('installserverclosed')
                except:
                    pass
    def getvid(self,id):#use
        '''used for getting frames from this instance's frames dictionary'''
        if id in self.frames:
            frame = self.frames[id].get()
            return frame
        else:
            return None
    def conn(self,d_id,c_id):#use
        '''this checks id's and asks to start udp stram to available port'''
        if d_id in self.clients:
            client = self.clients[d_id][0]
            c_id_list = self.clients[d_id][1]
            print('conn')
        else:
            return False
        if c_id in c_id_list:
            for i in self.portsavail:
                if i not in self.portsused:
                    self.portsused.append(i)
                    port = i
                    break
            
            command = ['udpstream',{'cam':c_id,'port':port}]
            print(command)
            data = pickle.dumps(command)
            datalen = struct.pack('I',len(data))
            print('sending command')
            try:
                client.sendall(datalen+data)
                data = pickle.loads(client.recv(2048))
                print('...',data)
                evi = threading.Event()
                thread = threading.Thread(target=self.updconn,args=(port,c_id,evi))
                thread.start()
                self.udps[c_id] = [evi,thread,client]
                return True
            except:
                print('hmm')
                self.frames[c_id].put(None)
                return False

            
        else:
            pass
    def udpstop(self,c_id):#use
        print('?stoping1')
        if c_id in self.udps:
            t = self.udps[c_id]
            t[0].set()
            t[1].join()
            size,data = self.structure(['udpstreamstop',{'cam':c_id}])
            t[2].sendall(size+data)
            del self.udps[c_id]
    def udpstopall(self):
        print('?stoping2')
        self.status = False
        for i in self.udps:
            t = self.udps[i]
            t[0].set()
            t[1].join()
            size,data = self.structure(['udpstreamstopall'])
            t[2].sendall(size+data)
        del self.udps 
    def stop(self):
        self.udpstopall()
        self.status = False
        print('stopped')
    def structure(self,msg):
        size = len(pickle.dumps(msg))
        size = struct.pack('I',size)
        return size,pickle.dumps(msg)
    def statusping(self):
        offcli = []
        for i in self.clients:
            client = self.clients[i][0]
            size,msg = self.structure(['statusping'])
            try:
                client.sendall(size+msg)
                data = pickle.loads(client.recv(2048))
                if data =='stillconnected':
                    pass
                else:
                    raise Exception
            except:
                c_id_list = self.clients[i][1]
                for c_id in c_id_list:
                    if cams.objects.filter(id = c_id):
                        cam = cams.objects.get(id = c_id)
                        cam.status = False
                        cam.save()
                device = devices.objects.get(id = i)
                device.status = False
                device.save()
                client.close()
                offcli.append(i)
        while len(offcli)>0:
            d_id = offcli.pop()
            del self.clients[d_id]
    def updconn(self,port,c_id,ev):
        maxdata = 2**16
        udpserv = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        udpserv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udpserv.bind((self.ip,port))
        print('udpstarted')
        self.buff(udpserv,maxdata)
        data = b''
        while not ev.is_set():
                try:
                    udpserv.settimeout(5)
                    seg, addr = udpserv.recvfrom(maxdata)
                    # udpserv.settimeout(None)
                    if struct.unpack('B', seg[0:1])[0] > 1:
                        data += seg[1:]
                    else:
                        data += seg[1:]
                        img = data
                        # img = cv2.imdecode(np.fromstring(data, dtype=np.uint8), 1)
                        # cv2.imshow('frame', img)
                        data = b''
                    self.frames[c_id].put(img)
                except KeyboardInterrupt:
                    self.stop()
                except Exception as e:
                    print(',',e)
                    if cams.objects.filter(id = c_id):
                        cam = cams.objects.get(id = c_id)
                        cam.status = False
                        cam.save()
                        frame = open('/home/uday/server/daemon/offline.jpg','rb').read()
                        self.frames[c_id].put(frame)
                        self.frames[c_id].put(frame)
                        self.frames[c_id].put(frame)
                        break
                    pass#################send client that it needs to restart
        else:   
            if c_id in self.frames:
                self.frames[c_id] = queue.Queue(maxsize=100)
            udpserv.close()
            if port in self.portsused:
                self.portsused.remove(port)
    def buff(self,s,maxdata):
        while True:
            seg, addr = s.recvfrom(maxdata)
            print(seg[0])
            if struct.unpack("B", seg[0:1])[0] == 1:
                print('finish emptying buffer')
                break


    
    

