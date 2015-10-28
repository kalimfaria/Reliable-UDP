"""
  UDP: Implements UDP for a virtual network

  Author: Daniel Zappala, Brigham Young University
  
  This program is licensed under the GPL; see LICENSE for details.

"""

import struct
import sys
import threading

# delete the following two lines if you have Python 2.5 installed
sys.path.append(".")
from Queue import *

__all__ = [ "UDP", "UDPSocket", "NoNetwork", "BadAddress", "NoAvailablePorts",
            "AddressInUse", "AlreadyBound", "MustBeConnected", "SocketClosed"]

class UDP:
    """ Emulate UDP on a host. """
    def __init__(self):
        """ Initialize the UDP protocol."""
        self.protocol = 17
        self.network = None
        self.maxPort = 65536
        self.sem = threading.Semaphore()
        self.binding = {}
        self.ports = {}

    def networkLayer(self,layer):
        """ Create a link to the network layer """
        self.network = layer

    def bind(self,socket,sourceIP,sourcePort):
        """ Bind a socket to the requested source IP and source port.
        The user may specify an IP address of 0, in which case we
        should bind to the address for this node.  The user may also
        specify a port of 0, in which case we should bind to an
        available port.

        The result of the bind call is that any packets arriving at this
        node that have the destination IP and port that match the
        bound IP and port will be passed to the supplied socket.

        If there is no network layer configured, raise the NoNetwork
        exception.  If the user provides an IP address that is not the
        address for this node, then raise the BadAddress Exception.
        If there are no ports available, raise the NoAvailablePorts
        exception.

        Note: all access to memory that is shared among all sockets
        must be protected with a semaphore.

        """
        # TBD: check for network

        # TBD: assign IP address if currently zero

        # TBD: check IP address     

        # lock
        self.sem.acquire()

        # TBD: assign an available port if currently zero

        # TBD: bind the address and port to the supplied socket

        # unlock
        self.sem.release()
        
        return (sourceIP,sourcePort)

    def close(self,sourceIP,sourcePort):
        """ Remove the binding for a socket that has been closed."""
        self.sem.acquire()
        # TBD
        self.sem.release()

    def send(self,data,sourceIP,destIP):
        """ Send a UDP packet to the network layer. """
        self.network.send(data,self.protocol,sourceIP,destIP)

    def receive(self,data,sourceIP,destIP):
        """ Receive a UDP packet from the network layer.  Drop the
        packet if the checksum fails.  Otherwise, find the socket
        bound to the destination address and port and deliver the
        packet to that socket.  If no socket is bound to this address
        and port, drop the packet."""
        # convert to a UDP packet
        u = UDPPacket()
        try:        
            u.unpack(data)
        except:
            print "Exception: unpacking a UDP packet"
            print "  ",sys.exc_info()[0],sys.exc_info()[1]
            return

        # check the checksum
        if u.checksum(sourceIP,destIP):
            print "Notice: the UDP checksum failed"
            return

        # TBD: deliver to the appropriate socket
        self.sem.acquire()
        self.sem.release()

class UDPSocket:
    """ Emulate a UDP socket on a host."""
    def __init__(self,udp):
        self.udp = udp
        self.state = "open"
        self.sourceIP = None
        self.sourcePort = None
        self.destIP = None
        self.destPort = None
        self.buffer = Queue(10)

    # interface to transport layer
    def receive(self,data,sourceIP,sourcePort):
        """ Receive a packet from UDP for this socket.  If the socket
        is connected, then it can only accept packets from the
        destination specified in the call to connect.  If the packet
        is valid for this socket, then it is queued in a buffer, along
        with the source IP and source port.  The packet waits in the
        buffer until a recv() or recvfrom() call extracts it.  If
        there is no room in the buffer, the packet is dropped."""
        # TBD

    # binding and connecting
    def bind(self,(sourceIP,sourcePort)):
        """ Associate a local address and port with this socket.  This
        is the address and port on which the socket will accept
        packets."""
        # TBD
        
    def connect(self,(destIP,destPort)):
        """ Set the default address and port to which this socket will
        send packets.  Setup the incoming address and port so that
        only packets from this address and port are accepted."""
        # TBD
        
    def close(self):
        """ Close the socket.  Any binding must be removed and all future
        calls on this socket must fail."""
        # TBD

    # sending data
    def send(self,data):
        """ Send a UDP packet to the default destination.  If the
        socket has has not been bound, then it must be bound before
        the data is sent so that it can receive a reply.  Valid only
        if the socket has been connected."""
        # TBD
        return len(data)
            
    def sendto(self,data,(destIP,destPort)):
        """ Send a UDP packet to a specific destination.  If the
        socket has not been bound, then it must be bound before the
        data is sent so that it can receive a reply."""
        # TBD
        return len(data)

    def makePacket(self,data,destIP,destPort):
        """ Make a UDP packet. """
        u = UDPPacket()
        u.sourcePort = self.sourcePort
        u.destPort = destPort
        u.len = len(data) + 8
        u.data = data
        u.cksum = u.checksum(self.sourceIP,destIP)
        return u.pack()

    # receiving data
    def recv(self):
        """ Receive a UDP packet.  Get the data, source IP, and source
        port from the buffer.  Ignore the source IP and port and
        return just the data.  If no data is available, wait
        indefinitely for the next available packet."""
        # TBD
        
    def recvfrom(self):
        """ Receive a UDP packet.  Get the data, source IP, and source
        port from the buffer.  Return the data and a tuple of the
        source IP and source port.  If no data is available, wait
        indefinitely for the next available packet."""
        # TBD

class UDPPacket:
    """ Class to represent a UDP packet.  Converts the packet from a
    set of member variables into a string of bytes so it can be sent
    over the socket."""
    def __init__(self):
        """ Initialize the packet """
        # UDP packet
        self.sourcePort = 0
        self.destPort = 0
        self.len = 0
        self.cksum = 0
        self.data = ''

        # packing information
        self.format = "!HHHH"
        self.headerlen = struct.calcsize(self.format)

    def checksum(self,sourceIP,destIP):
        """ Do the UDP checksum over the pseudoheader, UDP header, and
        data, padded to a multiple of two bytes if necessary.  See the
        UDP RFC for details."""
        # form pseudoheader
        p = PseudoHeader()
        p.sourceIP = sourceIP
        p.destIP = destIP
        p.length = self.len

        # data padding
        pad = ''
        if len(self.data) % 2 == 1:
            pad = '\x00'

        return self.InternetChecksum(p.pack() + self.pack() + pad)

    def pack(self):
        """ Create a string from a UDP packet """
        string = struct.pack(self.format,self.sourcePort,self.destPort,
                             self.len,self.cksum)
        return string + self.data

    def unpack(self,string):
        """ Create a UDP packet from a string """
        # unpack the header fields
        (self.sourcePort,self.destPort,self.len,self.cksum) = struct.unpack(self.format,string[0:self.headerlen])
        # unpack the data
        self.data = string[self.headerlen:]

    def InternetChecksum(self,data):
        """ Compute the Internet Checksum of the supplied data.  The
        checksum is initialized to zero.  Place the return value in
        the checksum field of a packet.  When the packet is received,
        check the checksum by passing in the packet.  If the result is
        zero, then the checksum has not detected an error.
        """

        sum = 0
        # make 16 bit words out of every two adjacent 8 bit words in the packet
        # and add them up
        for i in range(0,len(data),2):
            if i + 1 >= len(data):
                sum += ord(data[i]) & 0xFF
            else:
                w = ((ord(data[i]) << 8) & 0xFF00) + (ord(data[i+1]) & 0xFF)
                sum += w

        # take only 16 bits out of the 32 bit sum and add up the carries
        while (sum >> 16) > 0:
            sum = (sum & 0xFFFF) + (sum >> 16)

        # one's complement the result
        sum = ~sum

        return sum & 0xFFFF

class PseudoHeader:
    """ Pseudoheader used in the UDP checksum."""
    def __init__(self):
        self.sourceIP = 0
        self.destIP = 0
        self.protocol = 17
        self.length = 0
        self.format = "!LLxBH"

    def pack(self):
        """ Create a string from a pseudoheader """
        string = struct.pack(self.format,self.sourceIP,self.destIP,
                             self.protocol,self.length)
        return string

class NoNetwork(Exception):
    """ Exception to raise when no network layer is configured."""
    pass

class BadAddress(Exception):
    """ Exception to raise when trying to bind to an IP address that is
    not associated with this host."""
    pass

class NoAvailablePorts(Exception):
    """ Exception to raise when there are no more available ports."""
    pass

class AddressInUse(Exception):
    """ Exception to raise when trying to bind to an (IP,port) that is
    already in use."""
    pass

class AlreadyBound(Exception):
    """ Exception to raise when trying to bind to a socket that is
    already bound."""
    pass

class MustBeConnected(Exception):
    """ Exception to raise when calling send() on a socket that isn't
    connected."""
    pass

class SocketClosed(Exception):
    """ Exception to raise when a method is called on a closed socket."""
    pass
