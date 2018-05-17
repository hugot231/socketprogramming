import sys
import os
import socket
import sendrecv

#name of file (uppercase is static)
FILE_NAME = "created_server.txt"

# the size of the file
SIZE_SIZE = 11

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
		print port;
		port = 0;

	# create the listening welcomeSocket
	try:
		welcomeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
		print "Welcome Socket:", welcomeSocket;
	except:
		print("FAILURE, socket error.")
	# Bind the socket to port #
	try:
		print "binding...";
		welcomeSocket.bind(('', port));
	except:
		print("FAILURE, socket binding error.")

	if (port == 0):
		try:
			port = welcomeSocket.getsockname()[1];
		except:
			print("FAILURE, port error.")
	return (welcomeSocket, port); # returns welcomeSocket & port


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


def receiveDataFile(dataSocket, fileName):
	# Get the file size message
	fileSizeMsg = recvAll(dataSocket, SIZE_SIZE);

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
		fileData = recvAll(dataSocket, numToRecv);

		# Save the data
		fileObj.write(fileData);

		# Count the bytes
		numBytesLeft -= len(fileData);

	# Close the file and the socket
	fileObj.close();


def doList():
	return [f for f in os.listdir('.') if os.path.isfile(f)];
#def doList

def doPutServer(controlSocket):

	fileName = receiveDataString(controlSocket);

	fileName = "server_" + fileName;

	(dataSocketListen, newPort) = makeSocket(0);

	sendDataString(controlSock, str(newPort));

	# Make it a welcome socket
	dataSocketListen.listen(1);

	# Accept the connection
	(dataSock, addr) = dataSockListen.accept();

	receiveDataFile(dataSocket, fileName);

	dataSock.close();
	dataSockListen.close();
#def doPutServer

def doGetServer(controlSocket):

	fileName = receiveDataString(controlSocket);

	(dataSocketListen, newPort) = makeSocket(0);

	sendDataString(controlSocket, str(newPort));

	# Make it a welcome socket
	dataSocketListen.listen(1);

	# Accept the connection
	(dataSock, addr) = dataSocetkListen.accept();

	sendDataFile(dataSock, fileName);

	dataSock.close();
	dataSocketListen.close();

def doGetServer(controlSock):

	fileName = receiveDataString(controlSock);

	(dataSocketListen, newPort) = makeSocket(0);

	sendDataString(controlSock, str(newPort));

	# Make it a welcome socket
	dataSocketListen.listen(1);

	# Accept the connection
	(dataSock, addr) = dataSocketListen.accept();

	sendDataFile(dataSock, fileName);

	dataSock.close();
	dataSocketListen.close();


def doLsServer(controlSock):

	(dataSocketListen, newPort) = makeSocket(0);

	sendDataString(controlSock, str(newPort));

	# Make it a welcome socket
	dataSocketListen.listen(1);

	# Accept the connection
	(dataSock, addr) = dataSocketListen.accept();

	files = doList();

	buffer = ', '.join(i for i in files);

	sendDataString(dataSocket, buffer);

	dataSocket.close();
	dataSockListen.close();

################################# server main program begins here
# check usage of arguments
if len(sys.argv) < 2:
	print("USAGE: " + sys.argv[0] + " <PORT NUMBER>");
	exit(-1)

portNum = int(sys.argv[1]);
print "Port Number: ", portNum;

welcomeSocket, newPort = makeSocket(portNum);


welcomeSocket.listen(1);


# loop forever
while 1:
	print("Server is Listening");
	# server waits on accept()
	# new socket crete
	controlSocket, addr = welcomeSocket.accept();

	# Reset the command
	command = ""

	###################REMOVE############

	print "Client connected: ",  addr;

	#command = receiveDataString(controlSocket);
	while command != "quit":

		command = sendrecv.recvMsg(controlSocket)

		if command == "put":
			print "The command was: ", command
			#doPutServer(controlSocket);

		elif command == "get":
			print "The command was: ", command
			#doGetServer(controlSocket);

		elif command == "ls":
			print "The command was: ", command
			#doLsServer(controlSocket);
		elif command == "quit":
			print "The command was: ", command
			controlSocket.close();

		else:
			print('No, it is a little lower than that')
