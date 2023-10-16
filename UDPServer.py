 # Import socket module
from socket import *
import sys  # In order to terminate the program
import random  # for random integer
import struct

# Define the expected packet format
format='! i h h 14s x x'

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
        
def packetA():
    packet, clientAddress = serverSocket.recvfrom(1024)
    # Verifies packet
    data_length, pcode, entity, data = struct.unpack(format, packet)
    data=data.decode().rstrip("\x00") #removes any trailing null characters 
    if (data_length != len(packet)) or (data != "Hello World!!!") or (pcode != 0) or (entity != 2):
        print("Verification failed")
    else:
        new_packet=makePacketA(pcode,entity)
        serverSocket.sendto(new_packet, clientAddress)
        #change phase to B 
        #phase='B'
def makePacketA(pcode,entity):
    # Making values in the packet
    repeat = random.randint(5, 20)
    udp_port = random.randint(20000, 30000)
    length = int_to_short(random.randint(50, 100))
    codeA = int_to_short(random.randint(100, 400))
    format="!IIHH"
    #make data part of packet
    data=struct.pack(format,repeat,udp_port,length,codeA)
    #make header part of packet 
    data_length=struct.calcsize(format)
    header=struct.pack('!IHH',data_length,pcode,entity)
    # Making the packet
    packet=header+data
    return packet,udp_port,repeat

# Assign a port number
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)

# Bind the socket to server address and server port
serverSocket.bind(("localhost", serverPort))
phase='A'
#continue  varaible to know when server job is done 
cont=True

while cont:
    match phase:
        case 'A':

        case 'B':
            format='ihhhi'
            packet, clientAddress = serverSocket.recvfrom(1024)
            data_length,pcode,entity,packetId,data=struct.unpack(format, packet)
           #ensure what the size the packet should be, using this for now 
           #
           #!! change later 
            if( len(packet) != struct.calcsize(format) ):
                print("Error: Packet length is not correct")
                break
            #verifies that the packet_id field is correct
            if(packetId<0 or packetId>repeat-1):
                print("Packet id is incorrect")
                break
            #ensure packets arrive in the correct order ???
            if(data_length!=len(data)+len(packetId) or pcode !=codeA or entity != 2 or (data!=0 and len(data)%4!=0) ):
                print("Packet is not in the right order")
                break
            #passes all testing, send ack package 
            rec_packet=struct.pack('ihhi',data_length,pcode,entity,packetId)
            serverSocket.sendto(rec_packet, clientAddress)
            recieived=False 
            while recieived==False:
                socket.settimeout(5)
                acked_packet_id, serverAddress = serverSocket.recvfrom(1024)
                if(acked_packet_id!=packetId):
                    serverSocket.sendto(rec_packet, clientAddress)
                else:
                    recieived=True
# Close the server socket (this part may need improvements for graceful termination)
serverSocket.close()
