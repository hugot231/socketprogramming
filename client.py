import sys
import os
import socket


# The size of the file size message
SIZE_SIZE = 11

PromptString = "FTP> ";

def getFileSizeMsg(size):

	# Convert the size into string
	strSize = str(size)

	# add 0's to the front of the strSize
	while len(strSize) < SIZE_SIZE:
		strSize = "0" + strSize;

	print("size: ", strSize);

	return bytes(strSize, "utf-8");

def makeSocket(port):

	if (port < 0):
		port = 0;

	print port;
	# Create a socket
	welcomeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);

	# Bind the socket to port
	welcomeSocket.welcomeSocket(('', port));

	if (port == 0):
		port = welcomeSocket.getsockname()[1];

	return (welcomeSocket, port);

def connectSocket(serverPort, serverName):
	# Create a TCP socket for sending the file
	#print serverName;
	#print serverPort;
	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);

	#bind the socket to port 3
	#clientSocket.bind(('', serverPort));

	# Connect to the server!
	clientSocket.connect((serverName, serverPort));

	return clientSocket;

def connectSocketFromCurrentSocket(currentSocket, serverPort):

	return connectSocket(currentSocket.gethostname(), serverPort);

#####################################################
# Sends the specified amount of data using
# the specified socket
# @param sendSock - the socket to use for sending
# @param sendBuff - the buffer to send
#####################################################
def sendAll(sendSock, sendBuff):

	# The number of bytes successfully sent
	numSent = 0

	# Keep sending until all is sent
	while len(sendBuff) > numSent:

		# Send as much as you can
		sendCount = sendSock.send(sendBuff[numSent:])

		# Break the loop on error
		if not sendCount:
			break

		# Count the bytes you sent
		numSent += sendCount

def sendDataString(cliSock, data):
	# Put the file size into the message
	fileSizeMsg = getFileSizeMsg(len(data));

	# Send the message!
	sendAll(cliSock, fileSizeMsg);

	sendAll(cliSock, bytes(data, "utf-8"));

def sendDataFile(cliSock, fileName):
	# Get the file size
	fileSize = os.path.getsize(fileName);

	# Put the file size into the message
	fileSizeMsg = getFileSizeMsg(fileSize);

	# Send the message!
	sendAll(cliSock, fileSizeMsg);

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
		sendAll(cliSock, fileData);

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

def outputPrompt(prompt):
	print(prompt);

def doPutClient(serverName, controlSock, fileName):
	sendDataString(controlSock, "put");

	sendDataString(controlSock, fileName);

	dataPort = int(receiveDataString(controlSock));

	dataSock = connectSocket(serverName, dataPort);

	sendDataFile(dataSock, fileName);

	print("SUCCESS! " + fileName + " was uploaded to the server!")

	dataSock.close();

def doGetClient(serverName, controlSock, fileName):
	sendDataString(controlSock, "get");

	sendDataString(controlSock, fileName);

	dataPort = int(receiveDataString(controlSock));

	dataSock = connectSocket(serverName, dataPort);

	fileName = "client_" + fileName;

	receiveDataFile(dataSock, fileName);

	print("SUCCESS! " + fileName + " was downloaded from the server!")

	dataSock.close();

def doLsClient(serverName, controlSock):
	sendDataString(controlSock, "ls");

	dataPort = int(receiveDataString(controlSock));

	dataSock = connectSocket(serverName, dataPort);

	buffer = receiveDataString(dataSock);

	dataSock.close();

	return buffer.split(',');

# check usage
if len(sys.argv) < 3:
	print("USAGE: " + sys.argv[0] + " <server_machine> <server_port>");
	exit(-1)

serverName = sys.argv[1];
serverPort = int(sys.argv[2]);

# Server loop
while True:
	userInput = raw_input(PromptString);

	#print ("PromptString\n");
	tokenList = userInput.split(' ');

	command = tokenList[0];

	if command == "put":
		#fileName = tokenList[1];
		controlSock = connectSocket(serverName, serverPort);
		doPutClient(serverName, controlSock, fileName);
		controlSock.close();

	elif command == "get":
		#fileName = tokenList[1];
		controlSock = connectSocket(serverName, serverPort);
		doGetClient(serverName, controlSock, fileName);
		controlSock.close();

	elif command == "ls":
		controlSock = connectSocket(serverName, serverPort);
		files = doLsClient(serverName, controlSock);
		controlSock.close();

		for eachf in files:
			print(eachf);

	elif command == "lls":
		files = doList();

		for eachf in files:
			print(eachf);

	elif command == "quit":
		print("disconnects from the server and exits");
		break;

	elif command == "help":
		#print help commands here
		print(" Help ");
	else:
		print('Error, enter "help" for a list of commands')
