import socket
import struct
import pickle
import threading
import numpy as np
import cv2
import queue



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
                    print('recving')
                    sizereq = data[0:self.recvsize]
                    data = data[self.recvsize:]
                    sizereq = struct.unpack('I',sizereq)[0]
                    while len(data) < sizereq:
                        data+= client.recv(1024)
                    print('recived')
                    data = pickle.loads(data)
                    if data['auth'] == 'namex':
                        client.send('granted'.encode())
                        name = data['id']
                        cams = data['cams']
                        self.clients[name]=[client,cams]
                        self.frames[name]=queue.Queue(maxsize=100)
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
    def getvid(self,id):#use
        # self.frames[id] = b''
        # self.conn(id,cam)
        # while True:######## find a termination var
        #     if self.frames[id] != b'':
        #         frame = self.frames[id]
        #         yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        if id in self.frames:
            frame = self.frames[id].get()
            return frame
        else:
            return None

    def conn(self,id,cam):#use
        client = self.clients[id][0]
        cams = self.clients[id][1]
        print('conn')
        if cam in cams:
            for i in self.portsavail:
                if i not in self.portsused:
                    self.portsused.append(i)
                    port = i
                    break
            
            command = ['udpstream',{'cam':cam,'port':port}]
            print(command)
            data = pickle.dumps(command)
            datalen = struct.pack('I',len(data))
            print('sending command')
            client.sendall(datalen+data)
            evi = threading.Event()
            thread = threading.Thread(target=self.updconn,args=(port,id,evi))
            thread.start()
            self.udps[id] = [cam,evi,thread]
        else:
            pass
    def udpstop(self,id,cam):#use
        print('?stoping1')
        if id in self.udps:
            t = self.udps[id]
            t[1].set()
            t[2].join()
            del self.udps[id]
    def udpstopall(self):
        print('?stoping2')
        for i in self.udps:
            t = self.udps[i]
            t[1].set()
            t[2].join()
        del self.udps
    
    def stop(self):
        self.udpstopall()
        self.status = False
        print('stopped')


    def updconn(self,port,id,ev):
        maxdata = 2**16
        udpserv = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        udpserv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udpserv.bind((self.ip,port))
        print('udpstarted')
        self.buff(udpserv,maxdata)
        data = b''
        while self.status:
            if not ev.is_set():
                try:
                    seg, addr = udpserv.recvfrom(maxdata)
                    if struct.unpack('B', seg[0:1])[0] > 1:
                        data += seg[1:]
                    else:
                        data += seg[1:]
                        img = data
                        # img = cv2.imdecode(np.fromstring(data, dtype=np.uint8), 1)
                        # cv2.imshow('frame', img)
                        data = b''
                    self.frames[id].put(img)
                except KeyboardInterrupt:
                    self.stop()
                except:
                    pass#################send client that it needs to restart
            else:   
                if id in self.frames:
                    del self.frames[id]
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


    
    

