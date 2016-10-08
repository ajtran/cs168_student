import utils
import client_split_messages as csm

import sys
import socket
import select

CACHE = ""

if __name__ == "__main__":
  name, ip, port = sys.argv[1], sys.argv[2], sys.argv[3]
  clientSocket = socket.socket()
  try:
    clientSocket.connect((ip, int(port)))
    clientSocket.send(csm.pad_message(name))
  except:
    print(utils.CLIENT_CANNOT_CONNECT.format(ip, port))

  while True:
    sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX)
    sys.stdout.flush()
    SOCKETLIST = [sys.stdin, clientSocket]
    ready_to_read,ready_to_write,in_error = select.select(SOCKETLIST,[],[])
    for _socket in ready_to_read:
      # receiving messages from the client...
      if _socket == clientSocket:
        data = _socket.recv(utils.MESSAGE_LENGTH)
        if not data:
          print(utils.CLIENT_WIPE_ME + utils.CLIENT_SERVER_DISCONNECTED.format(ip, port))
          sys.exit()
        CACHE += data
        if len(CACHE) >= utils.MESSAGE_LENGTH:
          data = CACHE[:utils.MESSAGE_LENGTH]
          CACHE = CACHE[utils.MESSAGE_LENGTH:]
          sys.stdout.write(data.rstrip(" ") + "\n")
          sys.stdout.flush()
      # writing messages to the client
      else:
        data = raw_input()
        # I think i have to include a delimiter so i know where each message end
        clientSocket.send(csm.pad_message(data))


