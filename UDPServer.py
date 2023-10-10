# Import socket module
from socket import * 
import sys # In order to terminate the program
import random #for random integer 
import struct 

# Convert an integer to a "short"
def int_to_short(x):
    # Ensure x is within the range of a 16-bit signed integer (-32768 to 32767)
    x = max(min(x, 32767), -32768)
    return x

#  Debugging error message
def check_server_response(response):
    data_len, pcode, entity = struct.unpack_from('!IHH', response)
    if pcode == 555:
        response = response[8:]
        print(response.decode())
        sys.exit()
    return

# Assign a port number
serverPort = 120000
serverSocket = socket(AF_INET, SOCK_DGRAM)

# Bind the socket to server address and server port
serverSocket.bind(("", serverPort))


while True:

	data_length, pcode, entity, data, clientAddress  = serverSocket.recvfrom(1024)
    # Verfies packet 
	if (data_length != len(data)) or (data != "Hello World!!!") or (pcode != 0) or (entity != 2):
		print("Verfication failed") 
		break
	
	# Making values in packet 
	repeat= random.randint(5, 20)
	udp_port=random.randint(20000, 30000)
	len = int_to_short(random.randint(50, 100))
	codeA = int_to_short(random.randint(100, 400))

	# Making the packet 
	packet = struct.pack("iiiiihh",data_length, pcode, entity, repeat, udp_port, len, codeA)
	
	serverSocket.sendto(packet.encode(), clientAddress)

serverSocket.close()  
sys.exit() #Terminate the program after sending the corresponding data
