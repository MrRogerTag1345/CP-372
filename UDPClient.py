# Import socket module
from socket import * 
import sys
import struct 

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
data = "Hello World!!!"
data_length = len(data)
pcode = 0
entity = clientPort
format='! i h h 16s'
# Making the packet , string must be in bytes so encoded
packet = struct.pack(format,data_length, pcode, entity,data.encode())
#print(packed_data.decode('utf-8'))
# Ensuring length of packet % 4 == 0
if(len(packet)) % 4 != 0: #can also do struct.calcsize(format)
    print(f"The len of the packet is:  {len(packet)} ")
    print("Error: Packet length is not divisble by 4")
    #clientSocket.close()

# Sending packet to server 
clientSocket.sendto(packet, (serverName, serverPort))

# Getting packet from server 
new_packet, serverAddress = clientSocket.recvfrom(2024)
format="! i i i i i h h"
data_length, pcode, entity, repeat, udp_port, length, codeA =  struct.unpack(format, new_packet)
# Printing contents of packets 

print(f"Received packet from the server: data_len: {data_length} pcode: {pcode} entity: {entity} repeat:{repeat} len: {length} udp_port: {udp_port} codeA: {codeA} ")
print("----------- End Stage A -----------")
clientSocket.close()
