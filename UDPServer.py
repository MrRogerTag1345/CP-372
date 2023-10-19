 # Import socket module
from socket import *
import sys  # In order to terminate the program
import random  # for random integer
import struct

# Assign a port number
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
SEVERENTITY=2

#Here values for testing on sever from prof 
#serverName = '34.67.93.93'
#serverSocket.bind((serverName, serverPort)) 

# Bind the socket to server address and server port
serverSocket.bind(("", serverPort)) #can put local host in
#continue  varaible to know when server job is done 


#Methods for all

def getHeaderData(packet):
    #header is first 8 bit, rest is data 
    header=packet[:8]
    data=packet[8:]
    return header,data 

def decodeHeader(header):
	data_length, pcode, entity = struct.unpack("!IHH", header)
	return data_length, pcode, entity

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

#Methods for part A
def verPacketA():
    valid=True
    packet, clientAddress = serverSocket.recvfrom(1024)
    # Verifies packet
    data_length, pcode, entity, data = struct.unpack(format, packet)
    data=data.decode().rstrip("\x00") #removes any trailing null characters 
    if (data_length != len(packet)) or (data != "Hello World!!!") or (pcode != 0) or (entity != 2):
        print("Verification failed")
        valid=False
    return valid,data_length,pcode,entity,data,clientAddress
 
        
def makePacketA(pcode):
    # Making values in the packet
    entity=SEVERENTITY
    repeat = random.randint(5, 20)
    udp_port = random.randint(20000, 30000)
    length = int_to_short(random.randint(50, 100))
    codeA = int_to_short(random.randint(100, 400))
    #make data part of packet
    data=struct.pack("!IIHH",repeat,udp_port,length,codeA)
    #make header part of packet 
    data_length=struct.calcsize("!IIHH")
    header=struct.pack('!IHH',data_length,pcode,entity)
    # Making the packet
    packet=header+data
    return packet,udp_port,repeat,codeA

#Methods for part B

def makeAckPacket(codeA,ID):
    pcode=codeA
    packetID=ID
    #data is ID which is an integer from 0 to random 
    data_length=struct.calcsize("!I")
    data=struct.pack("!I",packetID)
    entity=SEVERENTITY
    header=struct.pack('IHH',data_length,pcode,entity)
    packet=header+data
    return packet

def makePacketB(pcode):
    data_length=struct.calcsize("!II")
    entity=SEVERENTITY
    tcp_port=random.randint(20000, 30000)
    codeB=random.randint(100, 400)
    header=struct.pack('IHH',data_length,pcode,entity)
    data=struct.pack("!II",tcp_port,codeB)
    packet=header+data
    return packet,codeB,tcp_port

#Methods for part C
#Methods for part D


def main():
    phase='A'
    while phase=='A':
        try:
            print("Waiting for client Phase A packet.")
            packet, clientAddress = serverSocket.recvfrom(1024)
            header, data = getHeaderData(packet)
            data_length, pcode, entity = decodeHeader(header)
            # #verify packet is correct
            # validation = validatePacket(header, data, phase, 0, 0, 0) # len and char aren't used yet, so 0 is used as placeholders
            # if validation != 0: # return code is 0 if valid, otherwise invalid, terminate connection
            # 	break
            packet,udp_port,repeat,codeA=makePacketA(pcode)
            serverSocket.sendto(packet, clientAddress)
            #print("Send Packet")
            phase='B'
            #current ID for phase B 
            currentID=0
        except timeout:
            print("Client closing due to timeout, didn't recieve any packets.")
            break
    while(phase=='B'):
        try:
            print("Waiting for client Phase B repeat packaets")
            packet, clientAddress = serverSocket.recvfrom(1024)
            header, data = getHeaderData(packet)
            # #verify packet is correct
            # validation = validatePacket(header, data, phase, length, 0, codeA) # len and char aren't used yet, so 0 is used as placeholders
            # if validation != 0: # return code is 0 if valid, otherwise invalid, terminate connection
            # 	break
            data_length, pcode, entity = struct.unpack("!IHH", header)
            ID,data=struct.unpack(f"!4s{data_length-4}s",data) #-4 as ID is being taken out 
            #convert ID that was in bytes to int 
            ID=int.from_bytes(ID,'big')  #converting ID back to int from bytes 
            #bad ID 
            print(f"Received packet {ID} from client")
            if ID < 0 or ID >= repeat: #if repeat is 3, ID should be 0,1,2 so 3 would be wrong 
                print(f"Invalid packet_id. Packet id is {ID}, when the range is from 0 to {repeat-1}. Exiting and closing client connection.")
                break
            #makes sure correct IDs are in recieved in order from 0 to random-1
            if ID == currentID: #correct
                #
                print(f"Correct packet recieved (Packet ID: {ID}), sending ackowledge packet to client")
                codeA=pcode
                acked_packet=makeAckPacket(codeA,ID)
                serverSocket.sendto(acked_packet, clientAddress)
                currentID+=1
                print(f"Awknowedge packet {ID} has been send to client ")
            else: #packet recieved in the wrong order, client needs to send again 
                print(f"Valid packet_id, but recieved in the wrong order. Packet id is {ID}, when expected is {currentID}. Rejected packet and waiting for correct one.")
            if currentID == repeat: #all packets for repeat has been send and verfied, countinue 
                #makes packet for phase B 
                packet,codeB,tcp_connection=makePacketB(codeA)
                #sends to client 
                serverSocket.sendto(packet, clientAddress) # send TCP port to client in phase b-2 packet
                #make Phase C TCP SOCKET connection
                severTCPSocket= socket(AF_INET, SOCK_STREAM)
                severTCPSocket.bind(("", serverPort))
                # Listen to at most 1 connection at a time
                severTCPSocket.listen(5) #from TCP example file 
                print ('The TCP server is ready to receive')
                phase = "C"
                break
              
        except timeout:
            print("Client closing due to timeout, didn't recieve any packets.")
            break
    serverSocket.close()
if __name__ == "__main__":
    main()
