# Import socket module
from socket import * 
import sys
import struct 

# Debugging error message
def check_server_response(response):
    data_len, pcode, entity = struct.unpack_from('!IHH', response)
    if pcode == 555:
        response = response[8:]
        print(response.decode())
        sys.exit()
    return


# Printing starting stage A
print("----------- Starting Stage A -----------")
#assign server name 

# clientName = 'local'  <- unused for now 
serverName = '34.67.93.93'

# Assign a port number
clientPort = 2 #same as in class 
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.connect((serverName, serverPort))

# Make the packet contents 
data = 'Hello World!!!'
data_length = len(data)
pcode = 0
entity = clientPort

# Making the packet  
format_string = '20s'
packed_data = struct.pack(format_string, data.encode('utf-8'))

packet = struct.pack("iiip",data_length, pcode, entity, packed_data)

# Ensuring length of packet % 4 == 0
if(len(packet)) % 4 != 0:  # !!! note, change to calcsize later 
    print("Error: Packet length is not divisble by 0")
    clientSocket.close()

# Sending packet to server 
clientSocket.sendto(packet.encode(), (serverName, serverPort))

# Getting packet from server 
data_length, pcode, entity, repeat, udp_port, length, codeA =  clientSocket.recvfrom(12000)
# Printing contents of packets 
print(f"Received packet from the server: data_len: {data_length} pcode: {pcode} entity: {entity} repeat:{repeat} len: {length} udp_port: {udp_port} codeA: {codeA} ")
print("----------- End Stage A -----------")
clientSocket.close()