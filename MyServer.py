from socket import *
import sys
import math # for math.ceil
import time
# URL: http://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&ved=0CCwQFjAA&url=http%3A%2F%2Filab.cs.byu.edu%2Fcs460%2Fcode%2Frouter%2Flab2%2Fsrc%2Fudp.py&ei=4W2kUqzdMo-ThQe2toDQDQ&usg=AFQjCNEcetwPIwphJ4L6B1o_5Pvae4oknQ&sig2=e6kt-VK7sVNe3YHImRrwyQ&bvm=bv.57752919,d.ZG4
# the file this code has been taken from is in folder Assign2CN2
def InternetChecksum(data):
        sum = 0
        # make 16 bit words out of every two adjacent 8 bit words in the packet
        # and add them up
        for i in range(0,len(data),2):
            if i + 1 >= len(data):
                sum += ord(data[i]) & 0xFF
            else:
                w = ((ord(data[i]) << 8) & 0xFF00) + (ord(data[i+1]) & 0xFF)
                sum += w
        while (sum >> 16) > 0:
            sum = (sum & 0xFFFF) + (sum >> 16)
        return ~sum & 0xFFFF

variable = "" # variable to store the received data
newnum=1 # suffices as loop counter
sizeof_data_received = 1015 # hard code alert!
next = 0
try : 
	serverPort =  int(sys.argv[1])
	serverSocket = socket(AF_INET, SOCK_DGRAM)
	serverSocket.bind(('',serverPort))

	print "SERVER : ready"

	firsttime = 0
	expected = 0
	buffer1 = [] 
	counter = 0
	start = 0

	clientAddr = ["",1]
	serverSocket.settimeout(0.01) 
	while newnum:
		try:
			data, clientAddr = serverSocket.recvfrom(sizeof_data_received)
			checksum , d = data.split(" ",1)
			check = InternetChecksum (d)
			c = int (checksum)
			seqno, data = d.split(" ",1)
			seqnum = int (seqno) 
			counter = 1 + counter
			#print expected
			if ( seqnum == expected  and check == c ):
				if ( firsttime == 0 ):
					seqno, filename, sizestr, data = d.split(" ",3)
					newnum = math.ceil((float(sizestr))/1000 )
					variable = variable + data
					newnum = newnum-1
					expected = expected + 1
					firsttime = 1
				else:
					variable = variable + data
					newnum = newnum-1
					expected = expected + 1
				
			elif ( seqnum > expected ):
				buffer1.insert(next, d) # for reordering
				next = next + 1
			elif ( seqnum < expected and (counter - 1)% 4 != 0):
				counter = counter - 1 # ignore for duplicate
			if counter % 4 == 0 or newnum == 0  :# to ack the packets
				serverSocket.sendto(str(expected),(clientAddr[0],clientAddr[1]))
		except timeout:
			serverSocket.sendto(str(expected),(clientAddr[0],clientAddr[1]))
	serverSocket.close()
	end = time.clock()
	time = end - start 
	print "Time consumed : " + str( time )
	print "SERVER : Shutting Down"
	createFile = open(filename, "w")  #creating a new file to write data
	createFile.write(variable) #writing data to created file
	createFile.close()
except:
	print "Error. Usage: python MyServer.py Port &"
