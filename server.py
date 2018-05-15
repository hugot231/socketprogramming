import sys
import os
import socket

#name of file (uppercase is static)
FILE_NAME = "created_server.txt"

# the size of the file
SIZE_SIZE = 11

###################################################
# Takes the file size and puts it into a message
# defined by KHOA's protocol.
# @size - the size of the file
# @return - the message containing the file size
###################################################
def getFileSizeMsg(size):

	# Convert the size into string
	strSize = str(size)

	# Prepend the string with 's
	while len(strSize) < SIZE_SIZE:
		strSize = "0" + strSize

	print("size: ", strSize);

	return bytes(strSize, "utf-8");


def makeSocket(port):

	if (port < 0):
		port = 0;

	# Create a socket
	try:
		welcomeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
	except:
		print("FAILURE, socket error.")
	# Bind the socket to port 0
	try:
		welcomeSocket.bind(('', port));
	except:
		print("FAILURE, socket binding error.")

	if (port == 0):
		try:
			port = welcomeSocket.getsockname()[1];
		except:
			print("FAILURE, port error.")
	return (welcomeSocket, port);


def connectSocket(serverName, serverPort):
	# Create a TCP socket for sending the file
	try:
		welcomeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
	except:
		print("FAILURE, socket creation error.")
	# Connect to the server!
	try:
		welcomeSocket.connect((serverName, serverPort));
	except:
		print("FAILURE, connect to server error.")

	return welcomeSocket;


def connectSocketFromCurrentSocket(currentSocket, serverPort):
	try:
		return connectSocket(currentSocket.gethostname(), serverPort);
	except:
		print("FAILURE, error connecting to current socket")
#def connectSocket

#####################################################
# Sends the specified amount of data using
# the specified socket2
# @param sendSock - the socket to use for sending
# @param sendBuff - the buffer to send
#####################################################
def sendAll(sendSock, sendBuff):

	# The number of bytes successfully sent
	numSent = 0

	# Keep sending until all is sent
	while len(sendBuff) > numSent:

		# Send as much as you can
		try:
			sendCount = sendSock.send(sendBuff[numSent:])
		except:
			print("FAILURE, error sending data")
		# Break the loop on error
		if not sendCount:
			break

		# Count the bytes you sent
		numSent += sendCount


def sendDataString(cliSock, data):
	# Put the file size into the message
	try:
		fileSizeMsg = getFileSizeMsg(len(data));
	except:
		print("FAILURE, error getting file size")

	# Send the message!
	try:
		sendAll(cliSock, fileSizeMsg);
	except:
		print("FAILURE, error sending message size")

	try:
		sendAll(cliSock, bytes(data, "utf-8"));
	except:
		print("FAILURE, error sending message data")


def sendDataFile(dataSock, fileName):
	# Get the file size
	fileSize = os.path.getsize(fileName);

	# Put the file size into the message
	fileSizeMsg = getFileSizeMsg(fileSize);

	# Send the message!
	sendAll(dataSock, fileSizeMsg);

	# How many file bytes have been sent
	numSent = 0;

	# Open the file for reading
	fileObj = open(fileName, "rb");

	# Keep sending the file in small chunks until all is sent
	while numSent < fileSize:

		# Read the bytes
		fileData = fileObj.read(4096);

		# The file data
		if not fileData:
			break;

		# Send all the bytes
		sendAll(dataSock, fileData);

		# Count the bytes
		numSent += len(fileData);
	#while numSent < fileSize

	fileObj.close();


#########################################
# Receives the number of bytes specified
# @param recvSock - the socket from which
# to receive
# @param recvSize - how much to receive
# @return - the data received
########################################
def recvAll(recvSock, recvSize):

	# The buffer to store the received contents
	recvBuff = bytearray();
	joinList = bytearray();

	# Keep receiving until all is received
	while not len(recvBuff) == recvSize:

		# The receiver buffer
		buff = recvSock.recv(recvSize - len(recvBuff))

		# Connection issues or we are done
		if not buff:
			break

		# Save the received content
		recvBuff = joinList.join([recvBuff, buff]);

	return recvBuff;


def receiveDataString(cliSock):
	# Get the file size message
	fileSizeMsg = recvAll(cliSock, SIZE_SIZE);

	# Get the file size from the message
	fileSize = int(fileSizeMsg.decode("utf-8"));

	buffer = bytearray();
	joinList = bytearray();

	# How many bytes are there left to receive
	numBytesLeft = fileSize;

	# Keep receiving and saving until all is saved
	while numBytesLeft > 0:

		# How many bytes to receive
		numToRecv = 4096;

		# If we have less than 4096 bytes
		if numBytesLeft < 4096:
			numToRecv = numBytesLeft;

		# Get the data
		fileData = recvAll(cliSock, numToRecv);

		buffer = joinList.join([buffer, fileData]);

		# Count the bytes
		numBytesLeft -= len(fileData);

	return buffer.decode("utf-8");


def receiveDataFile(dataSock, fileName):
	# Get the file size message
	fileSizeMsg = recvAll(dataSock, SIZE_SIZE);

	# Get the file size from the message
	fileSize = int(fileSizeMsg.decode("utf-8"));
	print("filesize: ", fileSize);

	# How many bytes are there left to receive
	numBytesLeft = fileSize;

	# Open the file
	fileObj = open(fileName, "wb");

	# Keep receiving and saving until all is saved
	while numBytesLeft > 0:

		# How many bytes to receive
		numToRecv = 4096;

		# If we have less than 4096 bytes
		if numBytesLeft < 4096:
			numToRecv = numBytesLeft;

		# Get the data
		fileData = recvAll(dataSock, numToRecv);

		# Save the data
		fileObj.write(fileData);

		# Count the bytes
		numBytesLeft -= len(fileData);

	# Close the file and the socket
	fileObj.close();


def doList():
	return [f for f in os.listdir('.') if os.path.isfile(f)];
#def doList

def doPutServer(controlSock):

	fileName = receiveDataString(controlSock);

	fileName = "server_" + fileName;

	(dataSockListen, newPort) = makeSocket(0);

	sendDataString(controlSock, str(newPort));

	# Make it a welcome socket
	dataSockListen.listen(1);

	# Accept the connection
	(dataSock, addr) = dataSockListen.accept();

	receiveDataFile(dataSock, fileName);

	dataSock.close();
	dataSockListen.close();
#def doPutServer

def doGetServer(controlSock):

	fileName = receiveDataString(controlSock);

	(dataSockListen, newPort) = makeSocket(0);

	sendDataString(controlSock, str(newPort));

	# Make it a welcome socket
	dataSockListen.listen(1);

	# Accept the connection
	(dataSock, addr) = dataSockListen.accept();

	sendDataFile(dataSock, fileName);

	dataSock.close();
	dataSockListen.close();

def doGetServer(controlSock):

	fileName = receiveDataString(controlSock);

	(dataSockListen, newPort) = makeSocket(0);

	sendDataString(controlSock, str(newPort));

	# Make it a welcome socket
	dataSockListen.listen(1);

	# Accept the connection
	(dataSock, addr) = dataSockListen.accept();

	sendDataFile(dataSock, fileName);

	dataSock.close();
	dataSockListen.close();


def doLsServer(controlSock):

	(dataSockListen, newPort) = makeSocket(0);

	sendDataString(controlSock, str(newPort));

	# Make it a welcome socket
	dataSockListen.listen(1);

	# Accept the connection
	(dataSock, addr) = dataSockListen.accept();

	files = doList();

	buffer = ', '.join(i for i in files);

	sendDataString(dataSock, buffer);

	dataSock.close();
	dataSockListen.close();


# Sanity checks
if len(sys.argv) < 2:
	print("USAGE: " + sys.argv[0] + " <PORT NUMBER>");
	exit(-1)

portNumber = int(sys.argv[1]);

(welcomeSock, newPort) = makeSocket(portNumber);

# Make it a welcome socket
welcomeSock.listen(100);

# running throught the loop
while True:

	print("Server is Listening");

	#accept connection
	(controlSock, addr) = welcomeSock.accept();

	print "Client connected: " + addr;

	command = receiveDataString(controlSock);

	if command == "put":
		doPutServer(controlSock);

	elif command == "get":
		doGetServer(controlSock);

	elif command == "ls":
		doLsServer(controlSock);

	else:
		print('No, it is a little lower than that')

	controlSock.close();
