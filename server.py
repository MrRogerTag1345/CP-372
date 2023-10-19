 # Import socket module
from socket import *
import sys  # In order to terminate the program
import random  # for random integer
import struct
import time

# Assign a port number
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverENTITY=2
HEADER_LENGTH=8
BYTE=7
#Here values for testing on server from prof 
#serverName = '34.67.93.93'
#serverSocket.bind((serverName, serverPort)) 

# Bind the socket to server address and server port
serverSocket.bind(("", serverPort)) #can put local host in
TIMEOUT=5 #how long server waits for packet from server 
#continue  varaible to know when server job is done 

#Methods for all
# Ensures packet is valid, len, char, and code are passed as 0 arguments during phases where not needed
#returns error number if there is an error, otherwise true 
#connection will close if error occurs 
def validPacket(header, data, length, phaseCode, char, phase): 
	data_length, pcode, entity = decodeHeader(header)
	packetSize = HEADER_LENGTH + data_length
 	# Error 1: Packet size not divisble by 4
	if packetSize % 4 != 0:
		print(f"Packet size is not divisble by 4, size is: {packetSize}. Connection closed.")
		return 0
	# Error 2. Data is incorect corresponding to each phase 
	if phase == "A":
        #convert data to string, up to the 14 len as HELLOWORLD!!! has len of 14, removes the extra stuff
		receivedData = str(data.decode("utf-8"))[:14] #subscript 
		if receivedData != "Hello World!!!":
			print("Wrong data for phase A. Data needs to be Hello World!!! but is {receivedData}. Closing connection.")
			return 0
	elif phase == "B":
		# Data portion has all 0's ? 
		# Length of data is data_length + 4 (packed_id) ?
		if data_length < length:
			print(f"Current size of data: {data_length}, However must be greater or equel to {(4 + length)}.")
			return 0
		if not isinstance(data, bytes): # Check data type
			print("Data can only be type byte for phase B.")
			return 0
		# Check if bytes are zero or null that isn't part of packet_id (only in data portion)
		for i in range(4, data_length):
            #dataString = data.decode()
			if data[i] != 48 and data[i] != 0: #ascii value of 0 is 48
				print(f"Value at {i} index: {data[i]}\nBytes must all be zero in the data.")
				return 0
	elif phase == "D":
		actual_data = data.decode("utf-8")#turns back into string for decoding 
		# Check to see if the data has the specified character
		for c in actual_data:
			if c != char.decode("utf-8"):
				print(f"Only {char} should be used in data in phase D, however data has {c}.")
				return 0
		# Ensure data is at least of length len2 (which is the len parameter in this function, and calling the function passes len2)
		if data_length < length:
			print(f"Data length must be at least {length}, but actual length is {data_length} in phase D")
			return 0
    #packet size and data length alreaedy taken cared of 
	# Error 3. Ensure pcode(code of previous phase) and entitty (1) are correct 
	if entity != 1:
		print("Entity from client must be 1")
		return 0
	if  (phase == "B" or phase == "D" or phase == "A") and pcode != phaseCode:
		print(f"Pcode should be {phaseCode} for but got {pcode} in phase {phase}")
		return 0
	# Error 4. check if header was made and assign proper spacing 
	headerValues = [data_length,pcode,entity]
	for h in headerValues:
        #header into bit length 
		numBytes = (h.bit_length() + BYTE) // 8
		# Convert to bytes 
		numBytes= len(h.to_bytes(numBytes, "big"))
       #usigned short, check if it was made properly (numBytes should be 2)
		if h!=data_length: #checking pcode and 
			if numBytes > 2:
				if h==entity:
					print(f"entity should be size 2 as an unsign short, but was size {numBytes}")
				else:
					print(f"pcode should be size 2 as an unsign integer, but was size {numBytes}")
				return 0
        #unsigned integer, check if it was made properly (numByte should be 4)
		else: #checing data_length
			if numBytes > 4:
				print(f"data_length should be size 4 as an unsign integer, but was size {numBytes}")
				return 0		

	# Error 5. Was big endian used in data ?
	for i in range(data_length):
		byteChar = chr(data[i]) # Convert the byte to a character
        #converting the data to the big ednian value 
		hexValue = hex(ord(byteChar))[2:].zfill(2)
        #are they the same? if not error 
		if data[i] != int(hexValue, 16):
			print("Big endian was not used for one or more characters.")
			return 0
	return 1

def decodeHeader(header):
	data_length, pcode, entity = struct.unpack("!IHH", header)
	return data_length, pcode, entity

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
        
def createPacketA(pcode):
    # Making values in the packet
    entity=serverENTITY
    repeat = random.randint(5, 20)
    udp_port = random.randint(20000, 30000)
    length = int_to_short(random.randint(50, 100))
    codeA = int_to_short(random.randint(100, 400))
    #create data part of packet
    data=struct.pack("!IIHH",repeat,udp_port,length,codeA)
    #create header part of packet 
    data_length=struct.calcsize("!IIHH")
    header=struct.pack('!IHH',data_length,pcode,entity)
    # Making the packet
    packet=header+data
    return packet,udp_port,repeat,codeA

#Methods for part B
def createAckPacket(codeA,ID):
    pcode=codeA
    packetID=ID
    #data is ID which is an integer from 0 to random 
    data_length=struct.calcsize("!I")
    data=struct.pack("!I",packetID)
    entity=serverENTITY
    header=struct.pack('IHH',data_length,pcode,entity)
    packet=header+data
    return packet

def createPacketB(codeA):
    data_length=struct.calcsize("!II")
    entity=serverENTITY
    tcp_port=random.randint(20000, 30000)
    codeB=random.randint(100, 400)
    header=struct.pack('IHH',data_length,codeA,entity)
    data=struct.pack("!II",tcp_port,codeB)
    packet=header+data
    return packet,codeB,tcp_port

#Methods for part C
def createpacketC(codeB):
    data_length = struct.calcsize("!IIIc")
    pcode = codeB
    entity = serverENTITY
    repeat2 = random.randint(5, 20)
    len2 = random.randint(50, 100)
    codeC = random.randint(100, 400)
    char='D'
    char=char.encode()

    header = struct.pack("!IHH", data_length, pcode, entity) 
    data = struct.pack('!IIIc',repeat2, len2, codeC, char)
    packet = header + data
    return packet, codeC, char,repeat2

#Methods for part D
def createPacketD(codeC):
    data_length = struct.calcsize("!I")
    pcode = codeC
    codeD= random.randint(100, 400)
    entity = serverENTITY

    header = struct.pack("!IHH", data_length, pcode, entity)
    data = struct.pack("!I", codeD)

    packet = header + data
    return packet

def main():
    phase='A'
    while phase=='A':
        try:
            print("Waiting for client Phase A packet.")
            packet, clientAddress = serverSocket.recvfrom(1024)
            header, data = getHeaderData(packet)
            data_length, pcode, entity = decodeHeader(header)
            #verify packet is correct
            #header,data,data_length,code,char,phase
            validation = validPacket(header, data,data_length, 0, 0, phase) 
            if validation ==0: # return code is 0 if valid, otherwise invalid, terminate connection
                print("Bad validation for phase A, ending connection")
                break
            packet,udp_port,repeat,codeA=createPacketA(pcode)
            serverSocket.sendto(packet, clientAddress)
            #print("Send Packet")
            phase='B'
            #current ID for phase B 
            currentID=0
            #create new UDP port using udp_port
		    # Bind the socket to new UDP port
            print(f"Making new UDP socket conneting with {udp_port} port")
            serverUDPSocket = socket(AF_INET, SOCK_DGRAM)
            serverUDPSocket.bind(("", udp_port))
            serverUDPSocket.settimeout(TIMEOUT) 
        except timeout:
            print("Client closing due to timeout, didn't recieve any packets.")
            break
    serverSocket.settimeout(TIMEOUT) 
    while(phase=='B'):
        try:
            print("Waiting for client Phase B repeat packaets")
            packet, clientAddress = serverUDPSocket.recvfrom(udp_port)
            header, data = getHeaderData(packet)
            print("Got a packet")
            # #verify packet is correct
            #header,data,data_length,code,char,phase
            validation = validPacket(header, data,data_length, codeA, 0, phase) # len and char aren't used yet, so 0 is used as placeholders
            if validation ==0: # return code is 0 if valid, otherwise invalid, terminate connection
                print("Bad validation for phase B, ending connection")
                break
            data_length, pcode, entity = struct.unpack("!IHH", header)
            ID,data=struct.unpack(f"!4s{data_length-4}s",data) #-4 as ID is being taken out 
            #convert ID that was in bytes to int 
            ID=int.from_bytes(ID,'big')  #converting ID back to int from bytes 
            #bad ID 
            print(f"Received packet {ID} from client")
            if ID < 0 or ID >= repeat: #if repeat is 3, ID should be 0,1,2 so 3 would be wrong 
                print(f"Invalid packet_id. Packet id is {ID}, when the range is from 0 to {repeat-1}. Exiting and closing client connection.")
                break
            #creates sure correct IDs are in recieved in order from 0 to random-1
            if ID == currentID: #correct
                #
                print(f"Correct packet recieved (Packet ID: {ID}), sending ackowledge packet to client")
                codeA=pcode
                acked_packet=createAckPacket(codeA,ID)
                serverUDPSocket.sendto(acked_packet, clientAddress)
                currentID+=1
                print(f"Awknowedge packet {ID} has been send to client ")
            else: #packet recieved in the wrong order, client needs to send again 
                print(f"Valid packet_id, but recieved in the wrong order. Packet id is {ID}, when expected is {currentID}. Rejected packet and waiting for correct one.")
            if currentID == repeat: #all packets for repeat has been send and verfied, countinue 
                #creates packet for phase B 
                packet,codeB,tcp_connection=createPacketB(codeA)
                #create Phase C TCP SOCKET connection
                print("Created TCP connection")
                serverTCPSocket= socket(AF_INET, SOCK_STREAM)
                serverTCPSocket.bind(("", tcp_connection))
                serverSocket.sendto(packet, clientAddress) # send TCP port to client 
                # Listen to at most 1 connection at a time
                serverTCPSocket.listen(TIMEOUT) #from TCP example file 
                #serverTCPSocket.timeout(TIMEOUT)
                connectionSocket, addr = serverTCPSocket.accept()
                print ('The TCP server is ready to receive')
                phase = "C"
                break
        except timeout:
            print("Client closing due to timeout, didn't recieve any packets.")
            break
    time.sleep(3)
    while(phase=='C'):
        try:
            packet,codeC,char,repeat2 = createpacketC(codeB)
            print("Packet Created")
            connectionSocket.send(packet)
            print("Send packet to client")
            phase='D'
        except timeout:
            print("Client closing due to timeout, didn't recieve any packets.")
            break
    numPackets=0
    if(phase=='D'):
        print(f"expected to recieve {repeat2} repeated packets from client")
        print(f"Range of packets: 0 - {repeat2-1}")
    while(phase=='D'):
        try:
            packet=connectionSocket.recv(1024)
            print(f"Received packet {numPackets}")
            numPackets+=1 
            time.sleep(1)
            #if got all the packets from server 
            if numPackets ==repeat2:
                #extract data 
                header,data=getHeaderData(packet)
                data_length,pcode,entity=decodeHeader(header)
                codeC=pcode
                
                #valdiate the data 
                # validation = validPacket(header, data,data_length, codeC, char, phase) 
                # if validation ==0: # return code is 0 if valid, otherwise invalid, terminate connection
                #     print("Bad validation for phase B, ending connection")
                #     break
                packet=createPacketD(codeC)
                time.sleep(1)
                connectionSocket.send(packet)
                phase='FINISH'
        except timeout:
            print("Client closing due to timeout, didn't recieve any packets.")
            break
    if(phase=='FINISH'):
        print("server has finish all phases")
    print("Closing TCP and UDP sockets")
    if (phase=='B'):
        serverUDPSocket.close()
    elif(phase =='C' or phase=='D'or phase=='FINISH'):
        #only close if they were open 
        serverTCPSocket.close()
        serverUDPSocket.close()
        connectionSocket.close()
    #always open
    serverSocket.close()
if __name__ == "__main__":
    main()
