#############################
# Sockets Server
#############################

import socket
import threading
from queue import Queue
from settings import SERVER_HOST, SERVER_PORT

def get_Host(): 
    try: 
        if SERVER_HOST != "":
              return SERVER_HOST
        else:
          host_name = socket.gethostname() 
          host_ip = socket.gethostbyname(host_name) 
          print("Hostname :  ",host_name) 
          print("IP : ",host_ip) 
          return host_ip
    except: 
        print("Unable to get Hostname and IP")

HOST = get_Host()
if SERVER_PORT != "":
  PORT = SERVER_PORT
else:
  PORT = 80
BACKLOG = 4

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((HOST,PORT))
server.listen(BACKLOG)            
print("looking for connection")
  
#Personal mail receptionist

def handleClient(client, serverChannel, cID, clientele):
  client.setblocking(1)
  msg = ""
  while True:
    try:
      msg += client.recv(10).decode("UTF-8")
      command = msg.split("\n")
      while (len(command) > 1):
        readyMsg = command[0]
        msg = "\n".join(command[1:])
        serverChannel.put(str(cID) + " " + readyMsg)
        command = msg.split("\n")
    except:
      print("Failed to connect")

#Takes message from bin and extracts important information, sending back to client

def serverThread(clientele, serverChannel):
  while True:
    msg = serverChannel.get(True, None)
    print("msg recv: ", msg)
    msgList = msg.split(" ")
    senderID = msgList[0]
    instruction = msgList[1]
    details = " ".join(msgList[2:])
    if (details != ""):
      for cID in clientele:
        if cID != senderID:
          sendMsg = instruction + " " + senderID + " " + details + "\n"
          clientele[cID].send(sendMsg.encode())
          print("> sent to %s:" % cID, sendMsg[:-1])
    print()
    serverChannel.task_done()
    
#Each client can be added 

clientele = dict()

#Line of users
serverChannel = Queue(100)
threading.Thread(target = serverThread, args = (clientele, serverChannel)).start()
clientNum= 0 

#Accepts new players to server

while True:
  client, address = server.accept()
  # myID is the key to the client in the clientele dictionary
  myID = clientNum
  for cID in clientele:
    clientele[cID].send(("newFriend %s\n" % myID).encode())
    client.send(("newFriend %s\n" % cID).encode())
  clientele[myID] = client
  client.send(("myIDis %s \n" % myID).encode())
  print("connection received from user %s" % myID)
  threading.Thread(target = handleClient, args = 
                        (client ,serverChannel, myID, clientele)).start()
  clientNum += 1
    