# Import necessary modules
from socket import *
import sys

# Create a TCP server socket
serverSocket = socket(AF_INET, SOCK_STREAM)

# Assign a port number
tcp_port = 12000  # Change this to your desired port

# Bind the socket to the server address and server port
serverSocket.bind(("", tcp_port))

# Listen to at most 5 connections at a time
serverSocket.listen(5)

print('The server is ready to receive')

while True:
    print('Waiting for a connection...')

    # Set up a new connection from the client
    connectionSocket, addr = serverSocket.accept()

    print(f'Connected to {addr}')

    # Receive data from the client
    sentence = connectionSocket.recv(1024).decode()

    if not sentence:
        # If no data is received, the client has closed the connection
        print(f'Connection with {addr} closed.')
        connectionSocket.close()
        continue

    # Capitalize the received message
    capitalizedSentence = sentence.upper()

    # Send the capitalized message back to the client
    connectionSocket.send(capitalizedSentence.encode())

    # Close the connection with the client
    connectionSocket.close()

# The serverSocket.close() line will only be executed when the server is explicitly terminated.
serverSocket.close()
sys.exit()  # Terminate the program
