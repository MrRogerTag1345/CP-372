 # Import socket module
from socket import *
import sys  # In order to terminate the program
import random  # for random integer
import struct

# Assign a port number
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)

# Bind the socket to server address and server port
serverSocket.bind(("localhost", serverPort))
#continue  varaible to know when server job is done 
cont=True

def getHeaderData(packet):
    #header is first 8 bit, rest is data 
    header=packet[:8]
    data=packet[8:]
    return header,data 

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
 
        
def makePacketA(pcode,entity):
    # Making values in the packet
    repeat = random.randint(5, 20)
    udp_port = random.randint(20000, 30000)
    length = int_to_short(random.randint(50, 100))
    codeA = int_to_short(random.randint(100, 400))
    #make data part of packet
    data=struct.pack("!IIHH",repeat,udp_port,length,codeA)
    #make header part of packet 
    data_length=struct.calcsize(format)
    header=struct.pack('!IHH',data_length,pcode,entity)
    # Making the packet
    packet=header+data
    return packet,udp_port,repeat,codeA

def makeAckPacket(data_length,pcode,entity,repeat):
    packetId=random.randint(0, repeat-1)
    header=struct.pack('IHH',data_length,pcode,entity)
    data=struct.pack("!I",packetId)
    packet=header+data
    return packet

def makePacketB(data_length,pcode,entity):
    tcp_port=random.randint(20000, 30000)
    codeB=random.randint(100, 400)
    header=struct.pack('IHH',data_length,pcode,entity)
    data=struct.pack("!II",tcp_port,codeB)
    packet=header+data
    return packet

def main():
    while cont:
        #Phase A
        valid,data_length,pcode,entity,data,clientAddress=verPacketA()
        if valid:
            packet,udp_port,repeat,codeA=makePacketA()
            serverSocket.sendto(packet, clientAddress)
            #Phase B
            clientPacket, clientAddress = serverSocket.recvfrom(1024)
            header,data=getHeaderData(clientPacket)
            data_length,pcode,entity=struct.unpack("IHH",header)
            packetId,data=struct.unpack("HI",data)
            #verfies ;en of packet is correct 
            valid=True
            if(len(packet) != struct.calcsize(format) ):
                print("Error: Packet length is not correct")
                valid=False
#           #verifies that the packet_id field is correct
            elif (packetId<0 or packetId>repeat-1):
                print("Packet id is incorrect")
                valid=False
            #ensure packets arrive in the correct order ???
            elif (data_length!=len(data)+len(packetId) or pcode !=codeA or entity != 2 or (data!=0 and len(data)%4!=0) ):
                print("Packet is not in the right order")
                valid=False
            #passes all testing, send ack package 
            if valid:
                awkPacket=makeAckPacket(data_length,pcode,entity,repeat)
                recieived=False 
                while recieived==False:
                    socket.settimeout(5)
                    acked_packet_id, clientAddress = serverSocket.recvfrom(1024)
                    if(acked_packet_id!=packetId):
                        serverSocket.sendto(awkPacket, clientAddress)
                    else:
                        recieived=True
                #makes actual packet now that awk package was send 
                packet=makePacketB(data_length,pcode,entity)
                serverSocket.sendto(awkPacket, clientAddress)
    # Close the server socket (this part may need improvements for graceful termination)
    serverSocket.close()
if __name__ == "__main__":
    main()
