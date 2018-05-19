import os
import socket

SIZE_SIZE = 10

def sendAll(sock, data):
 	# The number of bytes successfully sent
	numSent = 0

	# Keep sending until all is sent
	while len(data) > numSent:


		try:
			# Send as much as you can
			numSent = sock.send(data[numSent:])

		except socket.error:
			print "sendAll(): something happened to the connection"
			break

		# Break the loop on error
		#if not sendCount:
		#	break

		# Count the bytes you sent
		numSent += numSent

def recvAll(sock, numRecv):

	# The buffer to store the data
	data = ""

	while not numRecv == len(data):
		tempdata = sock.recv(numRecv - len(data))

		if not tempdata:
			break

		data += tempdata

	return data

#########################################
# Puts the data in a message and sends it
# @param sock - the socket to use
# @param data - the data to send
########################################
def sendMsg(sock, data):

	dataLen = len(data)
	stringData = str(dataLen);
	while (len(stringData) < SIZE_SIZE):
		stringData = "0" + stringData;

	sendAll(sock, stringData + data);

##################################################
# Receives a message defined by the structure
#  of a 10 byte length prefix and followed by the
# data.
# @param sock - the socket to use
##################################################
def recvMsg(sock):

	#call to receive first 10 bytes
	stringReceived = recvAll(sock, SIZE_SIZE);
	msgIntReceived = int(stringReceived);
	# call to receive the data portion of the msg
	data = recvAll(sock, msgIntReceived);

	return data


####################################################
# Generates a socket bound to an emphemeral port
# @return - the socket bound to the emphemeral port
####################################################
def getEphSocket():
	
	ephSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	# bind to port 0
	ephSocket.bind(('', 0))
	ephSocket.listen(1)
	
	return ephSocket

def sendFile(fileName, ephSocket):
	
	# The size of the file
	fileSize = os.path.getsize(fileName)
	
	# Send the file size
	sendMsg(ephSocket, str(fileSize))
	
	# Open the file
	fileObj = open(fileName, "r")
	
	# Keep reading the file until all is read
	while fileObj:
	
		# Read 1024 bytes
		fileData = fileObj.read(1024)
		
		# Make sure we did not hit the end of file	
		if fileData:
			sendAll(ephSocket, fileData)
		else:
			break
	
	fileObj.close()

##############################################
# Received a file from the TCP connection
# @param fileName - the name of the file
# @param ephSocket - the ephemeral socket
##############################################
def recvFile(fileName, ephSocket):
	
	# Get the file size (recvMsgs gets the string value)
	fileSizeStr  = recvMsg(ephSocket)
	
	# Convert the the size to int from fileSizestr
	fileSize = int(fileSizeStr)
	
	print "Size of the incoming file..."
	
	# Open the file for writing
	fileObj = open(fileName, "w")
	
	# The number of bytes received so far
	numRecvSoFar = 0
	
	# Keep receiving until all is received
	while fileSize > numRecvSoFar:
		
		# How much to receive
		numToRecv = 1024
		
		# Receive the right amount. Either 1024 bytes
		# or whatever is left
		if numToRecv < fileSize - numRecvSoFar:
			numToRecv = fileSize - numRecvSoFar
		
		# Receive the data
		data = recvAll(ephSocket, numToRecv)
		
		# Update the number of bytes received so far
		numRecvSoFar += len(data)
		
		# Save the data
		fileObj.write(data)	
			
	fileObj.close()

		
