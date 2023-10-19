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
SLEEP=1
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
        data =data.encode('utf-8')+bytearray(0*dataBitNeeded)
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

def PhaseA():
    print("----------- Starting Phase A -----------")
    packet,packet_len=makePacketA()
    valid=validPacketLen(packet,packet_len) #ensures packet is valid 
    if not valid:
        print("Packet making in client Phase A does not have size divisble by 4. Closing connecction.")
        print("----------- End Phase A -----------")
        clientSocket.close()
        sys.exit()
   #Sending packet to server 
    print("Sending packet to server")
    clientSocket.sendto(packet, (serverName, serverPort))
    # Getting packet from server 
    #gives server time to send packet 
    clientSocket.settimeout(TIMEOUT)
    try:
        serverPacket, serverAddress = clientSocket.recvfrom(2048) # Receive new packet from server
    except timeout:
        print("No packets has been received, connection may have ended. Closing connecction.")
        print("----------- End Phase A -----------")
        clientSocket.close()
        sys.exit()
    #print("Server send packet")
    #getting data from header and data section of packet 
    header,data=getHeaderData(serverPacket)
    repeat, udp_port, length, codeA =  struct.unpack("!IIHH",data)
    data_length,pcode,entity =  struct.unpack("!IHH",header)

    # Printing contents of packets 
    print(f"Received packet from the server: data_len: {data_length} pcode: {pcode} entity: {entity} repeat: {repeat} len: {length} udp_port: {udp_port} codeA: {codeA} ")
    print("----------- End Phase A -----------")
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
    data=''.zfill(length)
    #print(data)
    #ensuring len of data is divisible by 4
    data,data_length=increaseDataByte(data)
    data_length=data_length+4 #4 is from packet ID 
    packetId=id
    #print(packetId)
    #turn into big endian (bytes )
    packetId=packetId.to_bytes(4,'big')
    #make header and data of packet 
    data=packetId+data
    #print(data)
    #print(data)
    packet=struct.pack(f'!IHH{data_length}s',data_length,codeA,entity,data)
    return packet

def PhaseB(repeat,length,codeA,udp_port):
    print("----------- Starting Phase B -----------")
    #print(udp_port)
    #print(f"{repeat} {length} {codeA}")
    #The clientshould use a retransmission interval of at least 5 seconds.

    len_successfulPackets=0
    ackedPacketArray = [] #stores successful packets 
    #sends repeat amount of packages 
    while(repeat>len_successfulPackets):
        time.sleep(SLEEP)
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
        print("----------- End Phase B -----------")
        return tcp_port

#Functions for Part C

def PhaseC(TCPSocket):
    time.sleep(TIMEOUT)
    print("----------- Starting Phase C -----------")
    print("Connecting to TCP connection")
    serverPacket = TCPSocket.recv(1024)
    header, data = getHeaderData(serverPacket)
    repeat2,length2,codeC,char = struct.unpack("!IIIc", data)
    data_length,pcode,entity=decodeHeader(header)
    print(f"Received packet from the server: data_len: {data_length} pcode: {pcode} entity: {entity} repeat2: {repeat2} len2: {length2} codeC: {codeC} char: {char} ")
    print("----------- Ending Phase C -----------")
    return codeC,char,length2
#Received packet from the server: data_len: 13 pcode: 88 entity: 2 repeat2 17 len2: 16 codeC: 77 char: b'M' 
#Functions for Part D

def PhaseD(TCPSocket,codeC,char,length2):
    print("----------- Starting Phase D -----------")
    packet=makePacketD(codeC,char,length2)
    print(f"Sending {length2} packets throught TCP connection to server range 0 - {length2-1}")
    for i in range(length2):
        print(f"Sending packet #{i}")
        TCPSocket.send(packet)
        #ensure dont sent too quick to reduce error margin
        #time 1 seems to be the most consistent to work with server 
    print("All packets has been sent")
    serverPacket=TCPSocket.recv(1024)
    header,data=getHeaderData(serverPacket)
    codeD = struct.unpack("!I", data)[0]
    data_length,pcode,entity=decodeHeader(header)
    print(f"Received packet from the server: data_len: {data_length} pcode: {pcode} entity: {entity} codeD: {codeD} ")
    print("----------- Ending Phase D -----------")
    return

def makePacketD(codeC,char,length2):
    pcode = codeC
    entity=ENTITY_CLIENT
    #extra chars needed to make data divisble by 4
    extraChars=(4-(length2%4))%4
    #characters into byte array * number of characters needed 
    data = bytearray([ord(char)] * (length2 + extraChars))
    #print(data)
    data_length=extraChars + length2
    packet=struct.pack(f"!IHH{data_length}s",data_length,pcode,entity,data)
    return packet 

def main():
    repeat,length,codeA,udp_port=PhaseA()
    tcp_port=PhaseB(repeat,length,codeA,udp_port)
    TCPSocket = socket(AF_INET, SOCK_STREAM)
    TCPSocket.connect((serverName, tcp_port))
    codeC,char,length2=PhaseC(TCPSocket)
    PhaseD(TCPSocket,codeC,char,length2)
    #Close connections when finished 
    print("Tasks done, closing TCP and UDP connections")
    clientSocket.close()
    TCPSocket.close()
    print("Exiting program")

if __name__ == "__main__":
    main()
    
    
