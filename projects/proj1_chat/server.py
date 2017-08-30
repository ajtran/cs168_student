import utils
import client_split_messages as csm

import sys
import socket
import select

SOCKETINFODICT = {}
CHANNELDICT = {}

def broadcast(serverSocket, currSocket, socketList, msg):
  for nextSocket in socketList:
    # check to send message only to peer... (so not the server and not self)
    if nextSocket != serverSocket and nextSocket != currSocket:
      try:
        nextSocket.send(csm.pad_message(msg))
      # broken socket connection, remove it from SOCKETLIST
      except:
        nextSocket.close()
        if nextSocket in SOCKETINFODICT.keys():
          del SOCKETINFODICT[nextSocket]
          socketList.remove(nextSocket)

def checkMessage(msg, currSocket, serverSocket):
  split_msg = msg.split(" ")
  # print all the listed channels
  if split_msg[0] == "/list":
    for channel in CHANNELDICT.keys():
      currSocket.send(csm.pad_message(utils.CLIENT_WIPE_ME + channel))
  # create new channel for client
  elif split_msg[0] == "/create":
    if len(split_msg) == 1:
      currSocket.send(csm.pad_message(utils.CLIENT_WIPE_ME + utils.SERVER_CREATE_REQUIRES_ARGUMENT))
    else:
      newChannel = split_msg[1]
      if newChannel in CHANNELDICT.keys():
        currSocket.send(csm.pad_message(utils.CLIENT_WIPE_ME + utils.SERVER_CHANNEL_EXISTS.format(newChannel)))
      else:
        SOCKETINFODICT[currSocket][1] = newChannel
        CHANNELDICT[newChannel] = [currSocket]
  # add client to specified channel
  elif split_msg[0] == "/join":
    if len(split_msg) == 1:
      currSocket.send(csm.pad_message(utils.CLIENT_WIPE_ME + utils.SERVER_JOIN_REQUIRES_ARGUMENT))
    else:
      currChannel = split_msg[1]
      if currChannel not in CHANNELDICT.keys():
        currSocket.send(csm.pad_message(utils.CLIENT_WIPE_ME + utils.SERVER_NO_CHANNEL_EXISTS.format(currChannel)))
      else:
        if SOCKETINFODICT[currSocket][1] == None:
          SOCKETINFODICT[currSocket][1] = currChannel
          CHANNELDICT[currChannel].append(currSocket)
        else:
          prevChannel = SOCKETINFODICT[currSocket][1]
          broadcast(serverSocket, currSocket, CHANNELDICT[prevChannel], utils.CLIENT_WIPE_ME + utils.SERVER_CLIENT_LEFT_CHANNEL.format(SOCKETINFODICT[currSocket][0]))
          CHANNELDICT[prevChannel].remove(currSocket)
          SOCKETINFODICT[currSocket][1] = currChannel
          CHANNELDICT[currChannel].append(currSocket)
        broadcast(serverSocket, currSocket, CHANNELDICT[currChannel], utils.CLIENT_WIPE_ME + utils.SERVER_CLIENT_JOINED_CHANNEL.format(SOCKETINFODICT[currSocket][0]))
  # invalid control command
  else:
    currSocket.send(csm.pad_message(utils.CLIENT_WIPE_ME + utils.SERVER_INVALID_CONTROL_MESSAGE.format(msg)))

if __name__ == "__main__":
  serverSocket = socket.socket()
  serverSocket.bind(("localhost", int(sys.argv[1])))
  serverSocket.listen(5)

  SOCKETINFODICT[serverSocket] = ["Server", None, ""]
  
  print("Chat is ready to go!")

  while True:
    ready_to_read,ready_to_write,in_error = select.select(SOCKETINFODICT.keys(),[],[],0)

    for currSocket in ready_to_read:
      if currSocket == serverSocket:
        newSocket, address = serverSocket.accept()
        print("Client (%s, %s) just connected to this server." %address)
        SOCKETINFODICT[newSocket] = ["", None, ""]
      else:
        try:
          # receive data, if its there; send it to errybody
          data = currSocket.recv(utils.MESSAGE_LENGTH)
          if data:
            SOCKETINFODICT[currSocket][2] += data
            if len(SOCKETINFODICT[currSocket][2]) >= 200:
              data = SOCKETINFODICT[currSocket][2][:utils.MESSAGE_LENGTH].rstrip(" ")
              SOCKETINFODICT[currSocket][2] = SOCKETINFODICT[currSocket][2][utils.MESSAGE_LENGTH:]
              if SOCKETINFODICT[currSocket][0] == "":
                SOCKETINFODICT[currSocket][0] = data
              elif data[0] == "/":
                checkMessage(data, currSocket, serverSocket)
              else:
                currChannel = SOCKETINFODICT[currSocket][1]
                if currChannel == None:
                  currSocket.send(csm.pad_message(utils.CLIENT_WIPE_ME + utils.SERVER_CLIENT_NOT_IN_CHANNEL))
                else:
                  broadcast(serverSocket, currSocket, CHANNELDICT[currChannel], utils.CLIENT_WIPE_ME + "[" + SOCKETINFODICT[currSocket][0] + "] " + data)
          # if there is no data, assume connection is lost; remove from SOCKETLIST
          else:
            if currSocket in SOCKETINFODICT:
              # only tell people you are leaving if you are in the channel.. haha
              if SOCKETINFODICT[currSocket][1] != None:
                broadcast(serverSocket, currSocket, CHANNELDICT[SOCKETINFODICT[currSocket][1]], utils.CLIENT_WIPE_ME + utils.SERVER_CLIENT_LEFT_CHANNEL.format(SOCKETINFODICT[currSocket][0]))
              del SOCKETINFODICT[currSocket]
        # exception... but for what?
        except:
          if currSocket in SOCKETINFODICT:
            # only tell people you are leaving if you are in the channel.. haha
            if SOCKETINFODICT[currSocket][1] != None:
              broadcast(serverSocket, currSocket, CHANNELDICT[SOCKETINFODICT[currSocket][1]], utils.CLIENT_WIPE_ME + utils.SERVER_CLIENT_LEFT_CHANNEL.format(SOCKETINFODICT[currSocket][0]))
            del SOCKETINFODICT[currSocket]
          continue
  serverSocket.close()