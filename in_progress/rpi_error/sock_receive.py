#This code will be running on the LattePanda

import socket

UDP_IP = "0.0.0.0" # Listen on all interfaces
UDP_PORT = 5005 #arbitrary port number, but the port number must be the same as the sender

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT)) 

while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print("received message: %s" % data)