import sys
import socket


def runclient(server_host, server_port):
    server_addr = (server_host, server_port)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(server_addr)
    msg = "HELO {}".format(server_host)
    s.sendto(msg, server_addr)
    data = s.recv(1024)
    while True:
        try:
            msg = raw_input("Input> ")
            s.sendto(msg, server_addr)
            data = s.recv(1024)
            print("Server response: {}".format(data))
            res = data.split()
            if res[0] == "200" and res[1] == "BYE":
                print("Client exiting")
                break
        except:
            # Server probably disconnected. Exit.
            print("Client exiting")
            break


if __name__ == "__main__":
    try:
        runclient(sys.argv[1], int(sys.argv[2]))
    except ValueError:
        print("Port number must be an integer.")
    except IndexError:
        print("usage: python client.py <server-hostname> <server-port>")
