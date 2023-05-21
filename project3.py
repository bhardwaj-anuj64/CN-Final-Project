import socket
import math
import os 
import struct
import threading
from os import path

TCP_IP = "127.0.0.1"
Buffer_size = 1024

print("Greetings, welcome to the server")
# Get the name of the client
client_name = input("Enter your name:")
# Get the port number from the user
server_Port = int(input("Enter the port number you want to use:"))
# create a server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# create a client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

############################################################################################################
############################################Server side#####################################################

def server_start(server_Port):
    # bind the socket to the localhost ip address and port number
    server_socket.bind((TCP_IP, server_Port))
    while True:    
        # listen for connections
        server_socket.listen()
        # accept the connection
        conn_srvr, addr_client = server_socket.accept()
        conn_srvr.send(client_name.encode())
        conn_name = conn_srvr.recv(Buffer_size).decode()
        # create a thread to handle the connection
        client_thread = threading.Thread(target= client_handler, args=(conn_srvr,conn_name,))
        client_thread.start()
        
        
# create a thread to run the server
server_thread = threading.Thread(target= server_start, args=(server_Port,))
server_thread.start()

# create a function to handle the client connection
def client_handler(conn_srvr, conn_name):
    while True:
        # recieve the message from the client and decode it
        message_incoming = conn_srvr.recv(Buffer_size).decode()
        if "transfer" in str(message_incoming):
            #remove the upload string from the message_incoming string
            file_name = message_incoming[9:]
            # call the function to recieve the file
            recv_file(file_name, conn_srvr)
            # print the message from the client
            print(conn_name,": ", message_incoming)
        else:
            # print the message from the client
            print(conn_name,": ", message_incoming)
            continue

# create a function to recieve data when server recieved upload command from client
def recv_file(filename,conn_srvr):
    # recieve the filesize from the client
    filesize = struct.unpack("i",conn_srvr.recv(4))[0]
    # open a file with the recieved filename
    f = open(filename, 'wb')
    # recieve the file data from the client which the client will send in chunks of 1024 bytes
    for i in range(math.ceil(filesize/Buffer_size)):
        data = conn_srvr.recv(Buffer_size)
        # write the data to the file
        f.write(data)
    # close the file
    f.close()
    
    
############################################################################################################
############################################Client side#####################################################
 
# create a function to connect to the server 
def connect(TCP_PORT):
    try:
        #connect to the server
        client_socket.connect((TCP_IP, TCP_PORT))
        client_socket.send(client_name.encode())
        server_name = client_socket.recv(Buffer_size).decode()
        print("Connected to", server_name, "on port", TCP_PORT)
    except:
        print ("Connection failed, please try different port")
    
    
#create a function to upload a file to the server
def upload(filename):
    if not path.exists(filename):
        print("Error: File not found, please try again")
        return
    if path.exists(filename): 
        #open the file to be uploaded
        f = open(filename, 'rb')
        #send the filesize to the server in bytes
        client_socket.send(struct.pack("i",os.path.getsize(filename)))
        #send the file data to the server one chunk at a time
        for i in range(math.ceil(os.path.getsize(filename)/Buffer_size)):
            data = f.read(Buffer_size)
            client_socket.send(data)
        f.close()
        
        
        
# create a function to send a message to the server
def send_message(message_outgoing):
    # send the message to the server
    client_socket.send(message_outgoing.encode())
    


def user_start():
    # get the port number from the user
    TCP_PORT = int(input("Enter the port number you want to connect to:"))
    # connect to the server
    connect(TCP_PORT)
    # Create a loop to prompt the user for input
    while True:
        # Listen for a command
        message_outgoing = input("")
        if "transfer" in message_outgoing:
            #remove the upload string from the message_incoming string
            filename = message_outgoing.replace("transfer ","")
            # call the function to send the message
            send_message(message_outgoing)
            # call the function to upload the file
            upload(filename)
        else:
            # call the function to send the message
            send_message(message_outgoing)
            continue

# create a thread to prompt the user for input
user_start = threading.Thread(target= user_start)
user_start.start()
    

    
    