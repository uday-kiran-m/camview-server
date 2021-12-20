import servermod
import socket
import threading
import pickle
import time
import struct
daemon = servermod.server('cam.uday-server.com',5999)

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

def udpserv(id,cam,port,evudp):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1',port))
    s.listen()
    client,addr = s.accept()
    print(f'udp talking port:{port}')
    daemon.conn(id,cam)
    print(f'id:{id}')
    while not evudp.is_set():
        try:
            frame = daemon.getvid(id)
            if frame != None:
                # print('frame',daemon.frames)
                print(type(frame))
                size,msg = structure(frame)
                print(struct.unpack('I',size))
                client.sendall(size+msg)
        except BrokenPipeError:
            s.close()
            # print(id,cam)
            daemon.udpstop(id,cam)
            portsused.remove(port)
        except Exception as e:
            print(Exception==BrokenPipeError)
            print('mmm',e)
            evudp.set()
    else:
        s.close()
        daemon.udpstop(id,cam)
        portsused.remove(port)

def daemontalk(ev):
    commands = {'listconn':'listconn()','cams':'cams({})','udpstream':'manual'}
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1',5998))
    s.listen()
    print('ready to talk')
    client = ''
    while not ev.is_set():
            try:
                s.settimeout(5)
                client,addr = s.accept()
                print(f'conn talk {addr}')
            except:
                pass
            s.settimeout(None)
            if client != '':
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
                                client= ''
                            else:
                                print('f2')
                                ret = exec(commands[data].format(data[1]))
                                # print(data[1])
                                # ret = cams(data[1])
                                client.send(ret)
                                client.close()
                                client = ''

                        else:
                            print('udpserv..')
                            for i in ports:
                                if i not in portsused:
                                    evudp = threading.Event()
                                    t = threading.Thread(target=udpserv,daemon=True,args=(data[1],data[2],i,evudp))
                                    udps[data[1]] = [data[2],evudp,i]
                                    print(f'port :{i}')
                                    portsused.append(i)
                                    t.start()
                                    client.send(pickle.dumps([True,i]))
                                    client.close()
                                    client = ''
                                    break
                                    
                                else:
                                    client.send(pickle.dumps([False]))
                                    client.close()
                                    client = ''

                    else:
                        print('hmm')
                        client.send(pickle.dumps([False]))
                        client.close()
                        client=''
                except:
                    client.close()
                    client = ''
    else:
        s.close()
        print('stop daemon')
        



if __name__ == '__main__':
    ev = threading.Event()
    t = threading.Thread(target=daemontalk,daemon=True,args=(ev,))
    d = threading.Thread(target=daemon.start,daemon=True,)
    d.start()
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
    except Exception as e:
        print(e)