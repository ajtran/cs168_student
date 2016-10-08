import sys
import socket

if __name__ == "__main__":
  server_socket = socket.socket()
  server_socket.bind((sys.argv[1] , int(sys.argv[2])))
  print("Ready to go!")
  server_socket.listen(5)
  while True:
    (new_socket, address) = server_socket.accept()
    print(new_socket.recv(8))