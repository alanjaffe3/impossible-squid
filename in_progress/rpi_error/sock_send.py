#This code will be running on thr RPi

#Only uncomment threading if the the send/receieve it too frequent and other information is beign interrupted 
#import threading 
import subprocess
import socket

UDP_IP = "" #Enter the IP address of the computer you want to send data to
UDP_PORT = 5005 #arbitrary port number, but the port number must be the same as the receiver

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

cmd  = ["sudo", "journalctl", "-p", "err", "-b", "-f"]

proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

for line in proc.stdout:
    line = line.strip()
    if line: 
        print(line)
        sock.sendto(line.encode(), (UDP_IP, UDP_PORT))