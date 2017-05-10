import os
import sys
import threading
import socket
import datetime
from mailroom.mailroom import *
from mailroom.session import *

MAX_CONN = 16

class Server(object):
    def __init__(self, host, tcp_port, udp_port):
        self.host = host
        self.tcp = tcp_port
        self.udp = udp_port
        self.mailroom = MailRoom("db/")

    def get_response(self, state, addr, data):
        req = data.split()
        cmd = req[0]
        if cmd == "GET":
            response = ""
        return state, response
        
    def tcp_listen(self, conn, client_addr):
        session = MailSession(client_addr)
        session.parse_passkeys(self.mailroom.read_pass())
        while True:
            try:
                data = conn.recv(1024)
                if data:
                    print("Packet received: {}".format(data))
                    # LOG
                    # with open("db/.server_log", 'a') as f:
                    #    f.write("{} {} {} {}\n".format(datetime.datetime.now(), client_addr[0], host, data))
                    res = session.process_line(data)
                    print("Sending response: {}".format(res))
                    conn.sendall(res)
                    # LOG
                    #with open("db/.server_log", 'a') as f:
                    #    f.write("{} {} {} {}\n".format(datetime.datetime.now(), host, client_addr[0], res))
                    if session.state == AUTH_FIRST: 
                        self.mailroom.save_pass(session.user,
                                                session.passkeys[session.user])
                        session.state = TERMINATE
                        conn.close()
                    elif session.state >= SAVING:
                        if session.state == SAVING:
                            self.mailroom.save_email(session.target,
                                                     session.msg)
                            session.state = TERMINATE
                            conn.close()
                            break
                else:
                    conn.close()
                    break
            except:
                conn.close()
                break
    #
    # FIX THIS
    #
    def udp_server(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        addr = (self.host, self.udp)
        s.bind(addr)
        clients = {}
        while True:
            data, client_addr = s.recvfrom(1024)
            if not data:
                break
            if (client_addr not in clients.keys()):
                clients[client_addr] = START
            print("Packet received from {}: {}".format(client_addr, data))
            clients[client_addr], res = self.get_response(clients[client_addr], client_addr[0], "UDP", data)
            print("Sending response: {}".format(res))
            s.sendto(data, client_addr)
            if clients[client_addr] == terminate:
                clients[client_addr] = START
        s.close()
            

    def tcp_server(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        addr = (self.host, self.tcp)
        s.bind(addr)
        s.listen(MAX_CONN)
        while True:
            conn, client_addr = s.accept()
            conn.settimeout(60)
            threading.Thread(target = self.tcp_listen, args = (conn, client_addr)).start()

    def runserver(self):
        host = '127.0.0.1'
        #udp_server = threading.Thread(target = self.udp_server)
        tcp_server = threading.Thread(target = self.tcp_server)
        #udp_server.daemon = True
        tcp_server.daemon = True
        print("Starting threads. Type Q or Quit to quit.")
        #udp_server.start()
        tcp_server.start()
        while True:
            cmd = raw_input().lower()
            if cmd == "q" or cmd == "quit":
                sys.exit()

if __name__ == "__main__":
    try:
        Server('127.0.0.1', int(sys.argv[1]), int(sys.argv[2])).runserver()
    except IndexError:
        print("usage: python server.py <tcp-port-number> <udp-port-number>")
    except ValueError:
        print("Port numbers must be integers.")
