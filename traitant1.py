#! /usr/bin/python3
import os, sys

MAXBYTES = 100000 #reading 100ko max

data = os.read(0,MAXBYTES) #reading what client sent us in the socket

os.write(2,data) #writing to stderr what we read

if data[:3] == b"GET" and (data[6:14] == b"HTTP/1.1" or data[17:25] == b"HTTP/1.1"): #check if it's a GET request from a HTTP/1.1 client
    os.write(1,b"Request supported")
else:
    os.write(2,b"Request not supported\n")
    sys.exit(0)
