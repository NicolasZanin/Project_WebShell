#! /usr/bin/python3
import sys, os, time

def firstLine(data,char): #return the first line of GET request
    j = 0
    for i in data:
        if i == char:
            return data[:j]
        j += 1
    return -1

def findRequestGet(data,command,command2): #check if it's a request GET 
    return data[:3] == command and data[len(data)-9:-1] == command2

def findIndexCommand(data,char,string): #return the index of the command
    x,y = (-1,-1)
    for i in range(len(data)):
        if data[i] == char and x==-1:
            x = i+1
        if data[i:i+15] == string:
            y = i
    return x,y

def check(data,dataLenght): #check if new user by checking if link contains "ajoute_dans_session" action
    for i in range(dataLenght-20):
        if data[i:i+20] == "ajoute_dans_session_":
            return True
    return False 

def checkcommand(command,filename):
    if command == "clear":
        f_in = os.open(filename,os.O_RDONLY|os.O_TRUNC)
        os.close(f_in)
        return command
    elif command == "read":
        f_out = os.open("/tmp/read.txt",os.O_WRONLY|os.O_CREAT|os.O_TRUNC)
        os.write(f_out,b'1')
        os.close(f_out)
        return command + '\n'
    elif command == "echo $REPLY":
        f_out = os.open("/tmp/read.txt",os.O_RDONLY|os.O_CREAT)
        result = b''
        temp = os.read(f_out,1)
        while temp != b'':
            result+=temp
            temp = os.read(f_out,1)
        return command + '\n' + result.decode("utf-8")
    else:
        if os.path.isfile("/tmp/read.txt"):
            f_in = os.open("/tmp/read.txt",os.O_RDONLY)
            if os.read(f_in,1) == b'1':
                os.close(f_in)
                f_out = os.open("/tmp/read.txt",os.O_WRONLY)
                os.write(f_out,command.encode("utf-8") + b'\n')
                os.close(f_out)
                return command + '\n'
        return -1        
   
def escaped_latin1_to_utf8(s):#convert the string to utf-8
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

def reuseSession(temp): #reuse the session
    token=temp[25:30]
    filename="/tmp/logs_"+token+".txt"
    session="ajoute_dans_session_"+token
    return token,filename,session

def newSession(PORTC): #create a new session
    token=str(PORTC)
    filename="/tmp/logs_"+token+".txt"
    session="ajoute_dans_session_"+token
    traitant = "/tmp/FIFO"+token
    traitant2 = "/tmp/FIFO"+token+'2'
    # Make two FIFO
    os.mkfifo(traitant) # FIFO traitant to shell
    os.mkfifo(traitant2) # FIFO shell to traitant
    pid = os.fork()
    if pid==0:
        temp = os.environ["SHELL"] # where the shell is stock
        n = len(temp) - 1
        while temp[n] != "/": # Iteration for claim the name shell
            n-=1
        commandshell = temp[n+1:] # Get the name shell
        arg = f'{commandshell} {traitant} 3<> {traitant} &> {traitant2} 4< {traitant2}'
        args = [commandshell,"-c",arg]        
        os.execvp(args[0],args) # execute the shell persistant in the child
    return token,filename,session

def makeSession(firstline,lenfirstline):
    if not check(firstline,lenfirstline): #if the user is new
        token,filename,session=newSession(PORTC)
    else:
        #Using the session if the user is not new
        token,filename,session=reuseSession(firstline)
        if not os.path.isfile(filename):
            #Making new session if wrong token is used
            token,filename,session=newSession(PORTC)
    return token,filename,session

def commandfifo(token,command,filename):
    temp = checkcommand(command,filename)
    if temp != -1:
        return temp
    fd_out = os.open("/tmp/FIFO"+token,os.O_WRONLY) # open the fifo traitant to shell
    os.write(fd_out,command.encode("utf-8") + b'\n') # write the fifo traitant to shell
    os.write(fd_out,b'echo '+'Tpppp'.encode("utf-8")+b'\n') # Mark the end of command
    os.close(fd_out) # Close the fifo traitant to shell
    fd_in = os.open("/tmp/FIFO"+token+'2',os.O_RDONLY) # open the fifo shell to traitant with result command
    data = command.encode("utf-8") + b'\n'
    while not data.endswith(b'Tpppp\n'):
        data += os.read(fd_in,1)
    os.close(fd_in)
    data = data[:-6]
    return data.decode("utf-8")

MAXBYTES=100000 #max number of bytes to read
PORTC=int(sys.argv[1]) #port of the client


data = os.read(0,MAXBYTES)
data = data.decode("utf-8")
firstline = firstLine(data,'\n')

token,filename,session = makeSession(firstline,len(firstline))

header = b"HTTP/1.1 200\nContent-Type: text/html; charset=utf-8\nConnection: close\nContent-Length: 100000\n\n"
base = b"<!DOCTYPE html>\n<html>\n<head>\n\t<title>WebShell</title>\n</head>\n<body>\n"
form = b"\n\t<form action='"+session.encode("utf-8")+b"' method='get'>\n\t\t<input type='text' name='saisie' placeholder='Tapez quelque chose' />\n\t\t<input type='submit' name='send' value='&#9166;'>\n\t</form>\n</body>\n</html>"

if findRequestGet(firstline,"GET","HTTP/1.1"): #check if the request is a GET request
    x,y = findIndexCommand(firstline,'=',"&send=%E2%8F%8E") #find the index of the command "⏎"
    command=""
    logs=b""
    logs+=b"Session number : "+token.encode("utf-8")+b"<br>"
    date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()).encode("utf-8") #get the date
    if x !=-1 and y!=-1:
        command = escaped_latin1_to_utf8(firstline[x:y].replace('+',' ')) #open the log file of the current session
        command = commandfifo(token,command,filename)
        command = escaped_latin1_to_utf8(command)
    if not command == "":
        fd_out = os.open(filename,os.O_WRONLY|os.O_APPEND|os.O_CREAT) #open the log file of the current session
        os.write(fd_out,b'['+date+b"] "+command.encode("utf-8")+b'\n') #write history in the logs file
        os.close(fd_out)
    if os.path.isfile(filename):
        file = os.open(filename,os.O_RDONLY)
        reading = os.read(file,1000)
        while reading != b'': #catch the logs
            logs += reading
            reading = os.read(file,1000)
        logs = logs.decode("utf-8")
        logs = logs.replace('\n',"<br>") #replace the breaklines by <br>
        logs = logs.encode("utf-8")
    os.write(1,header+base+logs+form)
sys.exit(0)
