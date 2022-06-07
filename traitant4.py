#! /usr/bin/python3
import sys, os, time

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
    return res.decode("utf-8")

MAXBYTES=100000 #max number of bytes to read

data = os.read(0,MAXBYTES)
data = data.decode("utf-8")
firstline = firstLine(data,'\n')
header = b"HTTP/1.1 200\nContent-Type: text/html; charset=utf-8\nConnection: close\nContent-Length: 100000\n\n"
base = b"<!DOCTYPE html>\n<html>\n<head>\n\t<title>WebShell</title>\n</head>\n<body>\n"
form = b"\t<form action='ajoute' method='get'>\n\t\t<input type='text' name='saisie' placeholder='Tapez quelque chose' />\n\t\t<input type='submit' name='send' value='&#9166;'>\n\t</form>\n</body>\n</html>"


if findRequestGet(firstline,"GET","HTTP/1.1"): #check if the request is a GET request
    x,y = findIndexCommand(firstline,'=',"&send=%E2%8F%8E") #find the index of the command "⏎"
    command =""
    date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()) #get the date
    logs = b''
    if x !=-1 and y!=-1:
        command = escaped_latin1_to_utf8(firstline[x:y].replace('+',' ')) #convert the command sent to utf-8
    if not command == "":
        fd_out=os.open("logs.txt",os.O_WRONLY|os.O_APPEND|os.O_CREAT) #open the logs file
        os.write(fd_out,b'['+date.encode("utf-8")+b"] "+command.encode("utf-8")+b'\n') #write history in the logs file
        os.close(fd_out)
    if os.path.isfile("logs.txt"):
        fd_out=os.open("logs.txt",os.O_RDONLY)
        reading = os.read(fd_out,1)
        while reading != b'': #catch the logs
            logs+=reading
            reading = os.read(fd_out,1)
        os.close(fd_out)
        logs = escaped_latin1_to_utf8(logs.decode("utf-8").replace('\n','<br>\n')).encode("utf-8")
    os.write(1,header+base+logs+form) #send the page
sys.exit(0)
