#! /usr/bin/python3
import os, sys

def firstLine(data,char): #return the first line of GET request
    j = 0
    for i in data:
        if i == char:
            return data[:j]
        j += 1
    return -1

def findRequestGet(data,command,command2): #check if the command is in the data
    return data[:3] == command and data[len(data)-9:-1] == command2

def findIndexCommand(data,char,string): #return the index of the command
    x,y = (-1,-1)
    for i in range(len(data)):
        if data[i] == char and x==-1:
            x = i+1
        if data[i:i+15] == string:
            y = i
    return x,y

def escaped_latin1_to_utf8(s): #convert the string to utf-8
    res = b''
    i = 0
    while i < len(s):
        if s[i] == '%':
            res += int(s[i+1:i+3], base=16).to_bytes(1, byteorder='big')
            i += 3
        else :
            res += bytes(s[i], encoding='utf-8')
            i += 1
    return res.decode('utf-8')

MAXBYTES = 100000 #reading 100ko max

data = os.read(0,MAXBYTES) #read the data
data = data.decode("utf-8")
firstline = firstLine(data,'\n')
header = b"HTTP/1.1 200\nContent-Type: text/html; charset=utf-8\nConnection: close\nContent-Length: 2000\n\n"
base = b"<!DOCTYPE html>\n<html>\n<head>\n\t<title>WebShell</title>\n</head>\n<body>"
form = b"\n\t<form action='ajoute' method='get'>\n\t\t<input type='text' name='saisie' placeholder='Tapez quelque chose' />\n\t\t<input type='submit' name='send' value='&#9166;'>\n\t</form>\n</body>\n</html>"

if findRequestGet(firstline,"GET","HTTP/1.1"): #check if the request is a GET request
    x,y = findIndexCommand(firstline,'=',"&send=%E2%8F%8E") #find the index of the command
    command =""
    if x !=-1 and y!=-1:
        command = escaped_latin1_to_utf8(firstline[x:y].replace('+',' ')) #convert the string to utf-8
    os.write(1,header+base+b"\n\t<pre>\n"+data.encode("utf-8")+b"\t</pre>"+command.encode("utf-8")+form) #send the page
sys.exit(0)
