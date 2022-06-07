#! /usr/bin/python3
import os,sys

MAXBYTES = 100000 #reading 100ko max
data = os.read(0,MAXBYTES) #reading what client sent us in the socket

header =b"HTTP/1.1 200\nContent-Type: text/html; charset=utf-8\nConnection: close\nContent-Length: 1000\n\n"
content1 = b"Bonjour le monde! <br>Coma va, Nizza?"
content2 = b"<pre>" + data + b"</pre>"
base=b"<!DOCTYPE html>\n<html>\n\t<head>\n\t\t<title>WebShell</title>\n\t</head>\n\t<body>\n"+ content2 +b"\n\t</body></html>"

if data[:3] == b"GET" and (data[6:14] == b"HTTP/1.1" or data[17:25] == b"HTTP/1.1"): #check if it's a GET request from a HTTP/1.1 client
    os.write(1,header+base) #send the page to the client
sys.exit(0)
