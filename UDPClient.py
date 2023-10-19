#Andy Vuong 210868730
#Chetas Patel


# Import socket module
from socket import * 
import sys
import struct 
import time 
import random  # for random integer
#assign server name 
HEADER_LENGTH=8
ENTITY_CLIENT=1
TIMEOUT=5 #how long client waits for packet from server 
#serverName = '34.67.93.93' # for proof server
serverName='localhost'
# Assign a port number
clientPort = 2 #same as in class 
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)
#clientSocket.connect((serverName, serverPort)) <- not needed as client
# socket will swap ports, no need for connection

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
        data =data.encode('utf-8')+bytearray(1*dataBitNeeded)
    data_length=len(data)+dataBitNeeded
        #len does not count null empty character (null), can't use len(data)
    #print(f"Length of data is {data_length}")
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
        sys.exit()
    # Sending packet to server 
    #print("Sending packet to server")
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
    #print("Server send packet")
    #getting data from header and data section of packet 
    header,data=getHeaderData(serverPacket)
    repeat, udp_port, length, codeA =  struct.unpack("!IIHH",data)
    data_length,pcode,entity =  struct.unpack("!IHH",header)

    # Printing contents of packets 
    print(f"Received packet from the server: data_len: {data_length} pcode: {pcode} entity: {entity} repeat: {repeat} len: {length} udp_port: {udp_port} codeA: {codeA} ")
    print("----------- End Stage A -----------")
    return repeat,length,codeA,udp_port
    
def makePacketA():
    # Make the packet contents 
    data,data_length=increaseDataByte("Hello World!!!")
    pcode = 0
    entity = ENTITY_CLIENT
    packet=struct.pack(f'!IHH{data_length}s',data_length, pcode, entity,data)
    #data already made in increaseDataByte 
    # Making the packet , string must be in bytes so encoded
    packetSize=data_length+HEADER_LENGTH
    #print(f"Packet size is: {packetSize}")
    return packet,packetSize

#Funtions for Part B


def makePacketB(id,length,codeA):
    # Initlaizing variables 
    pcode=codeA
    entity = ENTITY_CLIENT
    packetId=id
    #print(packetId)
    #turn into big endian (bytes )
    packetId=packetId.to_bytes(4,'big')
    data=''.zfill(length)
    #ensuring len of data is divisible by 4
    data,data_length=increaseDataByte(data)
    data_length=data_length+4 #4 is from packet ID 
    #make header and data of packet 
    data=packetId+data
    print(data)
    packet=struct.pack(f'!IHH{data_length}s',data_length,codeA,entity,data)
    return packet

def stageB(repeat,length,codeA,udp_port):
    print("----------- Starting Stage B -----------")
    print(udp_port)
    #print(f"{repeat} {length} {codeA}")
    #The clientshould use a retransmission interval of at least 5 seconds.
    clientSocket.settimeout(TIMEOUT) 
    len_successfulPackets=0
    ackedPacketArray = [] #stores successful packets 
    #sends repeat amount of packages 
    while(repeat>len_successfulPackets):
        try:
            packet=makePacketB(len_successfulPackets,length,codeA)
            clientSocket.sendto(packet, (serverName, udp_port))
            print(f"Sending package {len_successfulPackets}")
            acked_packet, serverAddress = clientSocket.recvfrom(2024)
            print(f"{len_successfulPackets} packets has been acknowledged")
            header,data=getHeaderData(acked_packet)
            #print(f"{header} {data}")
            ack_id=struct.unpack('!I',data)[0] #only need the first thing in data, ignore the rest
            print(f"Acknowledged packet ID: {ack_id}. Current repeat packet ID: {len_successfulPackets}")
            #increment by 1 and put into array 
            len_successfulPackets+=1
            ackedPacketArray.append(acked_packet)
        #an unsuccessful try was done
        except timeout:
            print(f"Acknowledgement packet #{len_successfulPackets} was not send to client. Trying again")
        #due to while loop, tries again until gone through 0-random packets 
    #get packet from server once gone through all repeats and all has been valid 
    if len(ackedPacketArray) == repeat:
        print(f"All  {repeat} packets has been ackowledge")
        #get packet from server 
        serverPacket, serverAddress = clientSocket.recvfrom(2024)
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
    repeat,length,codeA,udp_port=stageA()
    tcp_port=stageB(repeat,length,codeA,udp_port)
    stageC(tcp_port)
    clientSocket.close()

if __name__ == "__main__":
    main()
    
    
