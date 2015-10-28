from socket import * 
import sys
import math
import threading
from threading import Semaphore
import time
import sys

#from BadNet0 import *
#from BadNet1 import *
#from BadNet2 import *
#from BadNet3 import *
#from BadNet4 import *
from BadNet5 import *

def InternetChecksum(data):
	sum = 0
	for i in range(0,len(data),2):
		if i + 1 >= len(data):
			sum += ord(data[i]) & 0xFF
		else:
			w = ((ord(data[i]) << 8) & 0xFF00) + (ord(data[i+1]) & 0xFF)
			sum += w
	while (sum >> 16) > 0:
		sum = (sum & 0xFFFF) + (sum >> 16)
	return ~sum & 0xFFFF
   

class myThread (threading.Thread):
	
	try :
		serverIP =  sys.argv[1] # getting arguments from the command line
		serverPort =  int(sys.argv[2])
		myfile =  sys.argv[3]
		send_base = 0
		window_size = 8
		next = 0
		t = ""
		fo = open(myfile, "r") # opening the file to read the data
		t = fo.read() # data stored in t
		fo.close() # closing the file	
	except:
		sys.exit("Error. Usage: python MyClient.py IP Port Filename")
	t= myfile + " " + str(len(t))+" "+t
	splits=[t[x:x+1000] for x in range(0,len(t),1000)] #HARD CODE ALERT!
	size = len(splits)
	seqnum = 0
	semaphore = Semaphore(0)
	sem2 = Semaphore(0)
	p = 0
	while size:
		data =  str(seqnum) + " " + splits[seqnum]
		checksum = InternetChecksum(data)
		check = str(checksum)
		splits[seqnum] =  check + " " + data
		seqnum += 1
		size -= 1	
	def __init__(self, threadID):
		threading.Thread.__init__(self)
		self.threadID = threadID
	def run(self):
		if (self.threadID == 1):
			iterator =  4
			length = math.ceil(len(myThread.splits)/4.0)
			while length: # looping through the data
				while iterator:
					BadNet.transmit(clientSocket, myThread.splits[myThread.p], myThread.serverIP, myThread.serverPort )
					myThread.p = myThread.p + 1
					iterator = iterator - 1
				myThread.sem2.release()
				myThread.semaphore.acquire()
				if ( myThread.p + 4 < len(myThread.splits) ):
					iterator = 4
				elif  ( myThread.p >= len(myThread.splits) ):
					iterator = 0
					break
				elif ( myThread.p + 4 >= len(myThread.splits) ) :
					iterator =len(myThread.splits) - myThread.p 
				length = math.ceil((len(myThread.splits) - myThread.p )/4.0)
		else :
			length = math.ceil(len(myThread.splits)/4.0)
			while length :		
				myThread.sem2.acquire()
				ACK, clientAddr = clientSocket.recvfrom(10)
				myThread.p = int(ACK)
				#print "ACK: " + ACK
				length = math.ceil((len(myThread.splits) - myThread.p )/4.0)
				myThread.semaphore.release()

print "CLIENT: Ready"
clientSocket = socket(AF_INET, SOCK_DGRAM) 			
thread1 = myThread(1)
thread2 = myThread(2)
thread1.start()
thread2.start()
thread1.join()
thread2.join()
print "CLIENT: Shutting Down"
clientSocket.close()	

