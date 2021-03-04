### DISTRIBUTED SYSTEMS | Assignment 1 ### Anette Sarivuo | 0544022 ###

import threading
import socket

# CLIENT FILE

NICKNAME = input("\nEnter nickname: ")
CHANNEL = input("\n### CHANNELS ####\n1) Finnish, 2) English, 3) Swedish.\nEnter channel number: ")

# Defining the connection (server)
HOST = "127.0.0.1" # local host IP address
PORT = 9876


# Connect the client to the server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

# Function for listening to server
def receiveMessages():
    while True:
        try:
            message = client.recv(1024).decode("utf-8")
            if (message == 'REQ_NICKNAME'):
                client.send(NICKNAME.encode("utf-8"))
            elif (message == 'REQ_CHANNEL'):
                client.send(CHANNEL.encode("utf-8"))
            else:
                # PRINT MESSAGE ONLY IN THE SELECTED CHANNEL
                print(message)
        except:
            print("Error in receiving the message. Closing the connection.")
            client.close()
            break
            
def writeMessages():
    while True:
        client.send(f'<{NICKNAME}> {input("")}'.encode("utf-8"))
        
recThread = threading.Thread(target=receiveMessages)
recThread.start()

writeThread = threading.Thread(target=writeMessages)
writeThread.start()