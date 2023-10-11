# Import socket module
from socket import *
import sys  # In order to terminate the program
import random  # for random integer
import struct

# Define the expected packet format
format = '!IHH'

# Convert an integer to a "short"
def int_to_short(x):
    # Ensure x is within the range of a 16-bit signed integer (-32768 to 32767)
    x = max(min(x, 32767), -32768)
    return x

# Debugging error message
def check_server_response(response):
    data_len, pcode, entity = struct.unpack(format, response)
    if pcode == 555:
        response = response[8:]
        print("Received response from the server:", response.decode())
        sys.exit()

# Assign a port number
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)

# Bind the socket to server address and server port
serverSocket.bind(("", serverPort))

while True:
    packet, clientAddress = serverSocket.recvfrom(1024)

    # Verifies packet
    data_length, pcode, entity, data = struct.unpack(format, packet)
    if (data_length != len(packet)) or (data != "Hello World!!!") or (pcode != 0) or (entity != 2):
        print("Verification failed")

    # Making values in the packet
    repeat = random.randint(5, 20)
    udp_port = random.randint(20000, 30000)
    length = int_to_short(random.randint(50, 100))
    codeA = int_to_short(random.randint(100, 400))
    
    print(data_length)
    print(pcode)
    print(entity)
    print(data)

    # Making the packet
    new_packet = struct.pack(format, data_length, pcode, entity, repeat, udp_port, length, codeA)

    serverSocket.sendto(new_packet, clientAddress)

# Close the server socket (this part may need improvements for graceful termination)
serverSocket.close()
