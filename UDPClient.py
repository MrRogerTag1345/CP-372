# Import socket module
from socket import * 
import sys
import struct 
import random  # for random integer
#assign server name 
HEADER_LENGTH=8
ENTITY_CLIENT=1
TIMEOUT=10 #how long client waits for packet from server 
#serverName = '34.67.93.93' # for proof server
serverName='localhost'
# Assign a port number
clientPort = 2 #same as in class 
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.connect((serverName, serverPort))

#Funtions for all

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

def decodeHeader(header):
	data_length, pcode, entity = struct.unpack("!IHH", header)
	return data_length, pcode, entity

def getHeaderData(packet):
    #header is first 8 bit, rest is data 
    header=packet[:8]
    data=packet[8:]
    return header,data 

def increaseDataByte(data):
    dataBitNeeded=4-len(data)%4
    if(dataBitNeeded!=0):
        #while not divisble, add a x00 [null string] to the end 
        #source: https://www.programiz.com/python-programming/methods/built-in/bytearray
        data =data.encode('utf-8')+bytearray(0*dataBitNeeded)
    data_length=len(data)+dataBitNeeded
        #len does not count null empty character (null), can't use len(data)
    return data,data_length

def validPacketLen(packet,packetLen):
    valid=True
    #lengthOfPacket=len(packet)
    if packetLen  % 4 != 0: #can also do struct.calcsize(format)
        print(f"The len of the packet is:  {len(packet)} ")
        print("Error: Packet length is not divisble by 4")
        valid=False
    return valid

#Functions for Part A 

def stageA():
    print("----------- Starting Stage A -----------")
    packet,packet_len=makePacketA()
    valid=validPacketLen(packet,packet_len) #ensures packet is valid 
    if not valid:
        print("Packet making in client phase A does not have size divisble by 4. Closing connecction.")
        print("----------- End Stage A -----------")
        clientSocket.close()
    #     sys.exit()
    # Sending packet to server 
    print("Sending packet to server")
    clientSocket.sendto(packet, (serverName, serverPort))
    # Getting packet from server 
    #gives server time to send packet 
    clientSocket.settimeout(TIMEOUT)
    try:
        serverPacket, serverAddress = clientSocket.recvfrom(2048) # Receive new packet from server
    except timeout:
        print("No packets has been received, connection may have ended. Closing connecction.")
        print("----------- End Stage A -----------")
        clientSocket.close()
        sys.exit()
    print("Server send packet")
    #getting data from header and data section of packet 
    header,data=getHeaderData(serverPacket)
    repeat, udp_port, length, codeA =  struct.unpack("!IIHH",data)
    data_length,pcode,entity =  struct.unpack("!IHH",header)
    # Printing contents of packets 
    print(f"Received packet from the server: data_len: {data_length} pcode: {pcode} entity: {entity} repeat:{repeat} len: {length} udp_port: {udp_port} codeA: {codeA} ")
    print("----------- End Stage A -----------")
    return repeat,length,codeA
    
def makePacketA():
    # Make the packet contents 
    data,data_length=increaseDataByte("Hello World!!!")
    pcode = 0
    entity = ENTITY_CLIENT
    header=struct.pack('!IHH',data_length, pcode, entity)
    #data already made in increaseDataByte 
    # Making the packet , string must be in bytes so encoded
    packet = header+data
    packetSize=data_length+HEADER_LENGTH
    return packet,packetSize

#Funtions for Part B

def makePacketB(repeat,length,codeA):
    # Initlaizing variables 
    pcode=codeA
    entity = ENTITY_CLIENT
    packetId=repeat
    data=''.zfill(length)
    #ensuring len of data is divisible by 4
    data,data_length=increaseDataByte(data)
    #make header and data of packet 
    header=struct.pack('!IHH',data_length,codeA,entity)
    data=struct.pack('!H',packetId)+data
    packet=header+data
    return packet

def stageB(repeat,length,codeA):
    # print("----------- Starting Stage B -----------")
    packet=makePacketB(repeat,length,codeA)
    clientSocket.sendto(packet, (serverName, serverPort))
    recieived=False 
    while recieived==False:
        socket.settimeout(5)
        acked_packet, serverAddress = clientSocket.recvfrom(2024)
        p_code,entity,acked_packet_id=struct.unpack('ihhi', acked_packet)
        #if no packet was received, send packet again 
        if(acked_packet_id==0):
            clientSocket.sendto(packet, serverAddress)
        else:
            recieived=True
            clientSocket.sendto(acked_packet_id, serverAddress)
    #get packet from server 
    serverPacket, serverAddress = clientSocket.recvfrom(2024)
    print("Server send packet")
    #getting data from header and data section of packet 
    header,data=getHeaderData(serverPacket)
    data_length, pcode, entity = decodeHeader(header)
    tcp_port,codeB =  struct.unpack("!II",data)
    print(f"Received packet from the server: data_len: {data_length} pcode: {pcode} entity: {entity} tcp_port: {tcp_port} codeB: {codeB} ")
    print("----------- End Stage B -----------")
    return tcp_port

#Functions for Part C

def stageC():
    return

#Functions for Part D

def main():
    repeat,length,codeA=stageA()
    tcp_port=stageB(repeat,length,codeA)
    stageC(tcp_port)
    clientSocket.close()

if __name__ == "__main__":
    main()
    
    
