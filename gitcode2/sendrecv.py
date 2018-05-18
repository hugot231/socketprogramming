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
