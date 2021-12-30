import servermod
import socket
import threading
import pickle
import time
import struct
from string import Template
daemon = servermod.server('25.61.109.117',5999)

udps = dict()

ports = range(6501,7001)
portsused = []
def listconn():
    return pickle.dumps(daemon.clients.keys())

def cams(id):
    return pickle.dumps(daemon.clients[id][1])

def structure(msg):
        size = len(pickle.dumps(msg))
        size = struct.pack('I',size)
        return size,pickle.dumps(msg)

def udpserv(d_id,c_id,port,evudp):
    global udps
    '''d_id->device id from db,\nc_id cam id from db,\nport -> port available,\nevudp->a thread event for udp stream'''
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1',port))
    s.listen()
    client,addr = s.accept()
    print(f'udp talking port:{port}')
    ret = daemon.conn(d_id,c_id)
    if ret:
        print(f'id:{d_id}')
    else:
        size,msg = structure(None)
        client.sendall(size+msg)
        evudp.set()
        time.sleep(1)
    while not evudp.is_set():
        try:
            frame = daemon.getvid(d_id)
            if frame != None:
                # print('frame',daemon.frames)
                # print(type(frame))
                size,msg = structure(frame)
                # print(struct.unpack('I',size))
                client.sendall(size+msg)
                # print('udpframing')
            else:
                size,msg = structure(frame)
                client.sendall(size+msg)
                break
        except Exception as e:
            print('mmm',e)
            evudp.set()
    else:
        s.close()
        daemon.udpstop(c_id)
        portsused.remove(port)

def daemontalk(ev):
    global udps
    commands = {'listconn':'listconn()','cams':'cams()','udpstream':'threading.Thread(target=udpserv,daemon=True,args=(d_id,c_id,port,evudp)).start()'}
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1',5998))
    s.listen()
    print('ready to talk')
    client = None
    while not ev.is_set():
            try:
                # print('waiting for conn')
                s.settimeout(5)
                client,addr = s.accept()
                print(f'conn talk {addr}')
            except:
                pass
            s.settimeout(None)
            if client != None:
                try:
                    data = pickle.loads(client.recv(2048))
                    print(data)
                    if data[0] in commands:
                        if data[0] != 'udpstream':
                            if len(data) ==1:
                                print('f1')
                                ret = exec(commands[data])
                                client.send(ret)
                                client.close()
                                client= None
                            else:
                                print('f2')
                                ret = exec(commands[data].format(data[1]))
                                # print(data[1])
                                # ret = cams(data[1])
                                client.send(ret)
                                client.close()
                                client = None

                        else:
                            print('udpserv..')
                            print(data)
                            for i in ports:
                                if i not in portsused:
                                    evudp = threading.Event()
                                    command = {'d_id':data[1],'c_id':data[2],'port':i,'evudp':evudp}
                                    # t = threading.Thread(target=udpserv,daemon=True,args=(data[1],data[2],i,evudp))
                                    t = commands[data[0]]
                                    exec(t,{'threading':threading,'udpserv':udpserv},command)
                                    udps[data[1]] = [data[2],evudp,i]
                                    print(f'port :{i}')
                                    portsused.append(i)
                                    # t.start()
                                    client.send(pickle.dumps([True,i]))
                                    client.close()
                                    client = None
                                    break
                                    
                            else:
                                client.send(pickle.dumps([False]))
                                client.close()
                                client = None

                    else:
                        print('hmm')
                        client.send(pickle.dumps([False]))
                        client.close()
                        client=None
                except Exception as e:
                    print(e)
                    client.close()
                    client = None
    else:
        s.close()
        print('stop daemon')
        
def stop(d_id):
    global udps
    evudp = udps[d_id][1]
    evudp.set()
    del udps[d_id]

def stopall():
    global udps
    for i in udps:
        evudp = udps[i][1]
        evudp.set()
    del udps

def statusping(ev):
    while not ev.is_set():
        time.sleep(15)
        print('pinging')
        daemon.statusping()
if __name__ == '__main__':
    ev = threading.Event()
    t = threading.Thread(target=daemontalk,daemon=True,args=(ev,))
    d = threading.Thread(target=daemon.start,daemon=True,)
    sp = threading.Thread(target=statusping,daemon=True,args=(ev,))
    d.start()
    sp.start()
    print('started daemon')
    t.start()
    print('start talk')
    try:
        while not ev.is_set():
            time.sleep(5)
    except KeyboardInterrupt:
        print('stopping')
        ev.set()
        t.join()
        daemon.stop()
        d.join()
        sp.join()
    except Exception as e:
        print(e)