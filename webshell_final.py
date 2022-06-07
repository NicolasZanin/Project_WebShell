#! /usr/bin/python3
import sys, os, time, json

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

def newSession(PORTC):
    token=str(PORTC)
    temp={
            "commands":[],
            "history":[]
    }
    with open("tokens.json","r") as f:
        jsondata=json.load(f)
        f.close()
    jsondata[token]=temp
    with open("tokens.json","w") as f:
        json.dump(jsondata,f,indent=4)
        f.close()
    jsondata=temp
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
    return token,jsondata,session

def reuseSession(firstline):
    token=firstline[25:30]
    session="ajoute_dans_session_"+token
    with open("tokens.json","r") as f:
        jsondata=json.load(f)
        f.close()
    return token,session,jsondata

def checkSession(data,dataLenght):
    for i in range(dataLenght-20):
        if data[i:i+20] == "ajoute_dans_session_":
            return True
    return False

def checkcommand(command,jsondata,token):
    if command == "clear":
        jsondata["history"] = []
        return command + '\n'
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
                os.write(f_out,command.encode("utf-8")+b'\n')
                os.close(f_out)
                return command + '\n'
        return -1      

def commandfifo(token,command):
    temp = checkcommand(command,jsondata,token)
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

MAXBYTES=800000
PORTC=int(sys.argv[1])

data = os.read(0,MAXBYTES)
data = data.decode("utf-8")
firstline = firstLine(data,'\n')
filename="tokens.json"
alert=""

if not checkSession(firstline,len(firstline)):
    token,jsondata,session=newSession(PORTC)
    alert="alert('Welcome to webshell, use arrow up and down to navigate history');"
else:
    token,session,jsondata=reuseSession(firstline)
    if str(token) not in jsondata:
        token,jsondata,session=newSession(PORTC)
        alert="alert('Welcome to webshell, use arrow up and down to navigate history');"
    else:
        jsondata=jsondata[token]

header =b"HTTP/1.1 200\nContent-Type: text/html; charset=utf-8\nConnection: close\nContent-Length: 100000000\n\n"
page1="""<!DOCTYPE html>
        <html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="https://iconarchive.com/download/i99290/froyoshark/enkel/iTerm.ico" title="shell">
    <title>Webshell</title>
    <style>
        body{
            color: #fff;
            background-color: #000;
            font-family: monospace;
            font-size: 1.5em;
            overflow-y: scroll;
        }
        #shell{
            margin: 0px 0px 90px 0px;
        }
        #shell:first-line{
            color: #ff0;
        }
        #commandInput{
            position: fixed;
            bottom: 0;
            width: 100%;
            background-color: #000;
        }
        input[type="text"],textarea{
            float: left;
            width: 80%;
            height: 50px;
            font-size: 25px;
            color:#fff;
            background-color: #000;
            margin-left: 10px;
            border:none;
        }
        input[type="submit"]{
            width: 3%;
            height: 50px;
            float:right;
            display:inline;
            margin-right: 10px;
            font-size: 1em;
            background-color: #000;
            border:none;
            color: #fff;
        }
        hr {
            border-color: green;
            border-width: 4px;
        }
        #arrow {
            margin-top: 5px;
            float:left;
            display:inline;
            border: solid green;
            border-radius: 5px;
            border-width: 0 7px 7px 0;
            padding: 14px;
            transform: rotate(-45deg);
            -webkit-transform: rotate(-45deg);
            animation-name: trigger;
            animation-duration: 1.5s;
            animation-iteration-count: infinite;
        }
        @keyframes trigger {
            from {border: solid green;
                border-width: 0 7px 7px 0;}
            to {border: solid black;
                border-width: 0 7px 7px 0;}
        }
    </style>
</head>
<body>
    <div id=shell>"""
page2="""</div>
    <div id="commandInput">
        <hr>
        <i id="arrow"></i>
        <form action='"""+session+"""'method="get">
            <input id="commandbox" type="text" name="command" placeholder="Command..." autocomplete="off"/>
            <input type="submit" name="send" value="&#9166;">
        </form>
    </div>
    <div id="bottom"></div>
    <script>
        var logs = """
page3=""";
        const commandbox = document.getElementById("commandbox");
        commandbox.focus();
        commandbox.select();
        var currentpos=logs.length-1;
        const input = document.querySelector("input");
        input.addEventListener("keyup", (event) => {
            if (event.key === 'ArrowUp') {
                if(currentpos>=0){
                commandbox.value=logs[currentpos];
                }
                if(currentpos>0){
                    currentpos--;
                }
            }
            if (event.key === 'ArrowDown') {
                if(currentpos<logs.length){
                    currentpos++;
                }
                if (currentpos<logs.length) {
                    commandbox.value=logs[currentpos];
                }
                else{
                    commandbox.value="";
                    currentpos=logs.length-1;
                }
            }
        });
        document.getElementById( 'bottom' ).scrollIntoView();"""
page4="""   </script>
</body>
</html>"""

if findRequestGet(firstline,"GET","HTTP/1.1"):
    x,y = findIndexCommand(firstline,'=',"&send=%E2%8F%8E")
    command=""
    logs=b""
    logs+=b"Session number : "+token.encode("utf-8")+b'\n'
    date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()).encode("utf-8")
    if x !=-1 and y!=-1:
        command = escaped_latin1_to_utf8(firstline[x:y].replace('+',' '))
        jsondata["commands"]+=[command]
        command = commandfifo(token,command)
        command = escaped_latin1_to_utf8(command)
    if not command == "":
        jsondata["history"]+=['['+date.decode("utf-8")+"] "+command]
    if os.path.isfile(filename):
        logs = logs.decode("utf-8")
        for i in jsondata["history"]:
            logs+=i
        logs = logs.replace('\n',"<br>\n")
        logs = logs.encode("utf-8")
        with open(filename,"r") as f:
            temp=json.load(f)
            f.close()
        temp[token]=jsondata
        with open(filename,"w") as f:
            json.dump(temp,f,indent=1)
            f.close()
    os.write(1,header+page1.encode("utf-8")+logs+page2.encode("utf-8")+str(jsondata["commands"]).encode("utf-8")+page3.encode("utf-8")+alert.encode("utf-8")+page4.encode("utf-8")+page4.encode("utf-8"))
