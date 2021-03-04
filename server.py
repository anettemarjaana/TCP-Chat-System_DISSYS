### DISTRIBUTED SYSTEMS | Assignment 1 ### Anette Sarivuo | 0544022 ###

import threading # for performing multiple tasks at once
import socket # for the network connection
from user import User # for creating user objects

# SERVER FILE

# Defining the connection
HOST = "127.0.0.1" # local host IP address
PORT = 9876

# Initializing the socket server. AF_INET for internet socket (instead of unix),
# SOCK_STREAM indicates the TCP protocol (instead of UDP)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen() # The socket is waiting for connections

clients = [] # connected clients
users = [] # clients' users including nickname and channel id

# BROADCASTING MESSAGES FROM THE SERVER TO CLIENTS
def broadcast(message, sender):
    if (sender != None): # Not a common message sent by the system
        senderIndex = clients.index(sender)
        senderUser = users[senderIndex]
        senderChannel = senderUser.channel
        
        if ("#HELP" in message): # INSTRUCTIONS CASE
        # print the instructions to the sender only
        
        # INSTRUCTIONS FOR:
            # LEAVING THE CHANNEL
            # PRIVATE MESSAGE: if user enters "to username: msg" only username can see the msg
            
            # Calculate the number of users online in the channels
            ch1 = ch2 = ch3 = 0
            for user in users:
                if (user.channel == "1"):
                    ch1 +=1
                elif (user.channel == "2"):
                    ch2 += 1
                elif (user.channel == "3"):
                    ch3 += 1
            
            message = f'\n ### INFORMATION ####\n Hi {senderUser.nickname}! You are on channel {senderChannel}.\n 1) Finnish: {ch1} users\n 2) English: {ch2} users\n 3) Swedish: {ch3} users\n\n### INSTRUCTIONS ####\n - To switch channel, enter #channelID (e.g. #1)\n - To send a private message, start your message with to: nickname (e.g. to: joey hello)\n'
            message = message.encode("ascii")
            sender.send(message)
        elif any(s in message for s in ["#1", "#2", "#3"]): # CHANNEL SWITCH CASE
            
            if ("#1" in message):
                senderChannel = "1"
            elif ("#2" in message):
                senderChannel = "2"
            elif ("#3" in message):
                senderChannel = "3"
                
            senderUser.switchChannel(senderChannel)
            
            print(f'Client {senderUser.nickname} moved to channel {senderChannel}')
            message = f'\nSwitched channel successfully! Welcome to the channel {senderChannel}. For more info and instructions, type #HELP\n'
            message = message.encode("ascii")
            sender.send(message)
        elif ("to: " in message): # PRIVATE MESSAGE CASE
        # check if the message is meant to be sent privately to someone
        # and only forward it to them.
            checker = 0 # checker for whether a message has been sent already
            
            if (len(users) > 1): # if there are more than 1 object in the users list
                for user in users:
                    # If this string is included in the message, 
                    # it is supposed to be privately sent to the user:
                    priv = "to: {}".format(user.nickname)
                    
                    if (priv in message):
                            
                        if (user.nickname == senderUser.nickname):
                            # The user can not send a private message to themselves.
                            userIndex = senderIndex
                            message = "Private message function failed: Can't send one to self."
                            message = message.encode("ascii")
                            sender.send(message)
                            checker = 1
                            break
                        
                        else:
                            userIndex = users.index(user)
                            privateMsg_client = clients[userIndex] # the corresponding client object
                            message = message.encode("ascii")
                            privateMsg_client.send(message)
                            checker = 1
                            break               
                                
                if (checker == 0): # userIndex returns false if no corresponding user found
                    message = "No such user online"
                    message = message.encode("ascii")
                    sender.send(message)
            else: # if the list equals to 1
                message = "Private message function failed: No other users online."
                message = message.encode("ascii")
                sender.send(message)
        else: # MESSAGE SENT BY A CLIENT IN A CHANNEL        
        # check which channel the message belongs to and only send it in that channel
            message = message.encode("ascii")
            
            # a list of the indexes in the clients that the msg should be sent to:
            sendTo = [] 
            
            for user in users:
                if (user.channel == senderChannel):
                    sendTo.append(users.index(user))
            sendTo.remove(senderIndex)
            for i in sendTo:
                clients[i].send(message)
   
    else:
        # If it's a common message to everyone from the system, then the sender is None
        message = message.encode("ascii")
        for client in clients:
            client.send(message)
    
# clientHandler is a loop running in a thread for each client
def clientHandler(client):
    while True: # an endless loop
        try:
            # message is received --> broadcast it to the clients
            # 1024 bytes message decoded for string comparison in broadcast function
            message = client.recv(1024).decode("ascii") 
            broadcast(message, client)
        except:
            # If the client produces an error --->
            # cut the connection for this client, remove the client
            # and terminate the loop
            clientIndex = clients.index(client)
            clientUser = users[clientIndex]
            
            print(f'Client {clientUser.nickname} left')
            broadcast("{} left".format(clientUser.nickname), client)
            
            users.remove(clientUser)
            
            clients.remove(client)
            client.close()
            break
       
# This function handles the new clients by accepting their connections
def receiveClientConnection():
    while True:
        client, address = server.accept()
        print(f'New client connected with address {str(address)}')
                
        clients.append(client) # add the new user in the clients object list
        
        # ask the new user for a nickname & channel and once received,
        # add it on the list as an object
        client.send('REQ_NICKNAME'.encode("ascii"))
        clientNickname = client.recv(1024).decode("ascii")
        
        client.send('REQ_CHANNEL'.encode("ascii"))
        clientChannel = client.recv(1024).decode("ascii")
        if (clientChannel not in ["1", "2", "3"]):
            # error, default choice Finnish:
            errorMsg = "Error, not valid choice. Default choice: channel 1 (Finnish)."
            client.send(errorMsg.encode("ascii"))
            clientChannel = 1
        
        # Add the new user in the users object list
        users.append(User(clientNickname, clientChannel))
        
        # Printed on server:
        print(f'Nickname of the new client is {clientNickname} and they join the channel {clientChannel}')
        
        # Printed to the new client only:
        welcomeMessage = f'Hi {clientNickname}! Welcome to the channel {clientChannel}. For more info and instructions, type #HELP\n'
        client.send(welcomeMessage.encode("ascii"))
        
        # Printed on the channel to everyone but the new client:
        broadcast("{} joined!".format(clientNickname), client)
        
        # Thread is started for each connection
        thread = threading.Thread(target=clientHandler, args=(client,))
        thread.start()

print("Server is listening ...\n")        
receiveClientConnection()