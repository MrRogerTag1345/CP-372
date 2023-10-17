# Import socket module
from socket import * 
import sys
import struct 
import random  # for random integer
#assign server name 
# clientName = 'local'  <- unused for now 
serverName = '34.67.93.93'
# Assign a port number
clientPort = 2 #same as in class 
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.connect((serverName, serverPort))

def getHeaderData(packet):
    #header is first 8 bit, rest is data 
    header=packet[:8]
    data=packet[8:]
    return header,data 

# def assignConnection():
#     #assign server name 
#     # clientName = 'local'  <- unused for now 
#     serverName = '34.67.93.93'
#     # Assign a port number
#     clientPort = 2 #same as in class 
#     serverPort = 12000
#     clientSocket = socket(AF_INET, SOCK_DGRAM)
#     clientSocket.connect((serverName, serverPort))
#     return serverName,clientPort,serverPort,clientSocket

<<<<<<< Updated upstream
def makePacketA():
    # Make the packet contents 
    data = "Hello World!!!"
    data=bytes(data,'utf-8')
    data_length = len(data)
    pcode = 0
    entity = clientPort
    header=struct.pack('!IHI',data_length, pcode, entity,)
    data=struct.pack('!14s',data)
    # Making the packet , string must be in bytes so encoded
    packet = header+data
    return packet
=======
# Getting packet from server 
new_packet, serverAddress = clientSocket.recvfrom(2024)
format="! i i i i i h h"
new_packet = new_packet[:24]
data_length, pcode, entity, repeat, udp_port, length, codeA =  struct.unpack(format, new_packet)
# Printing contents of packets 
>>>>>>> Stashed changes

def validPacketLen(packet):
    valid=True
    if(len(packet)) % 4 != 0: #can also do struct.calcsize(format)
        print(f"The len of the packet is:  {len(packet)} ")
        print("Error: Packet length is not divisble by 4")
        valid=False
    return valid

def stageA():
    print("----------- Starting Stage A -----------")
    packet=makePacketA()
    valid=validPacketLen(packet)
    if valid:
        # Sending packet to server 
        clientSocket.sendto(packet, (serverName, serverPort))
        # Getting packet from server 
        serverPacket, serverAddress = clientSocket.recvfrom(2024)
        print("Server send packet")
        #getting data from header and data section of packet 
        header,data=getHeaderData(serverPacket)
        repeat, udp_port, length, codeA =  struct.unpack("!IIHH",data)
        data_length,pcode,entity =  struct.unpack("!IHH",header)
        # Printing contents of packets 
        print(f"Received packet from the server: data_len: {data_length} pcode: {pcode} entity: {entity} repeat:{repeat} len: {length} udp_port: {udp_port} codeA: {codeA} ")
        print("----------- End Stage A -----------")

def main():
    stageA()
    clientSocket.close()

if __name__ == "__main__":
    main()
    
    
# print("----------- Starting Stage B -----------")
# # Initlaizing variables 
# pcode=codeA
# entity = clientPort
# packetId=random.randint(0, repeat-1)
# data=''.zfill(length)
# #ensuring len of data is divisible by 4
# while(len(data)%4!=0):
#     #while not divisble, add a 0 to the end 
#     data.bytearray(1)
# #convert to int from string 
# data=int(data)
# datalength=len(data)+len(packetId)
# format='ihhhi'
# # Making packet 
# packet = struct.pack(format,data_length,pcode,entity,packetId,data)
# # Sending packet to server 
# clientSocket.sendto(packet, (serverName, serverPort))
# recieived=False 
# while recieived==False:
#     socket.settimeout(5)
#     acked_packet, serverAddress = clientSocket.recvfrom(2024)
#     p_code,entity,acked_packet_id=struct.unpack('ihhi', new_packet)
#     #if no packet was received, send packet again 
#     if(acked_packet_id==0):
#         clientSocket.sendto(packet, (serverName, serverPort))
#     else:
#         recieived=True
#         clientSocket.sendto(acked_packet_id, serverAddress)
