# Import necessary modules
from socket import *
import random

# Define the server's IP address or hostname
serverName = 'localhost'  # Change this to the server's IP or hostname

# Assign a port number
tcp_port = 12000  # Change this to the same port as your server

# Create a packet
data = "Hello World!!!"
data_length = len(data)
codeB = 0
pcode = codeB
entity = tcp_port
repeat2 = random.randint(5, 20)
len2 = random.randint(50, 100)
CodeC = random.randint(100, 400)
char = 'B'

# Create a client socket
clientSocket = socket(AF_INET, SOCK_STREAM)

# Connect to the server
clientSocket.connect((serverName, tcp_port))

# Get user input
sentence = input('Input lowercase sentence: ')

# Send the user's input to the server
clientSocket.send(sentence.encode())

# Receive and print the server's response
modifiedSentence = clientSocket.recv(1024)
print('From server:', modifiedSentence.decode())

# Close the client socket
clientSocket.close()
