import sys
import socket

if __name__ == "__main__":
  client_socket = socket.socket()
  # TA's IP: 52.53.187.155 Port: 2013
  client_socket.connect((sys.argv[1], int(sys.argv[2])))
  client_socket.send(raw_input())
  sys.exit(1)