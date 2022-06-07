#! /usr/bin/python3
import os, sys, socket, signal, select, json, atexit

#Making the SIGINT signal to SIGINT every client connected to the server and the server itself
def handler(sig, ignore):
    global socketpid
    signal.signal(signal.SIGINT, signal.default_int_handler)
    for pid in socketpid:
        os.kill(pid[1], signal.SIGINT)
    mdir = "/tmp/"
    for fname in os.listdir(mdir):
        if fname.startswith("logs_"):
            os.remove(os.path.join(mdir, fname))
    with open("tokens.json","w") as f:
        json.dump({},f)
        f.close()
    sys.exit(0)
    
def endserver():
    for file in os.listdir("/tmp/"):
        if file.startswith("FIFO") or file == "read.txt":
            os.remove(os.path.join("/tmp/", file))

def delPid(socketpid,index,find): #Function to delete the pid from the list
    for i in range(len(socketpid)):
        if socketpid[i][index] == find:
            socketpid.pop(i)
            break 
    return socketpid

if __name__ == "__main__":

    #Server won't launch if there are less than 2 arguments
    if len(sys.argv) != 3:
        os.write(1,b"Please give the Traitant and the Port\n")
        sys.exit(0)

    #Checking the entries => Traitant and Port :

    #Check if the Traitant is a file
    if not os.path.isfile(sys.argv[1]) and sys.argv[1] != "cat":
        os.write(1,b"Traitant must be an existing file\n")
        sys.exit(0)

    #Check if the port is a number
    try:
        PORT = int(sys.argv[2])
    except ValueError:
        os.write(1,b"Port must be a number\n")
        sys.exit(0)
    
    #Check if the port is in the right range
    if PORT < 1024 or PORT > 65535:
        os.write(1,b"Port must be between 1024 and 65535\n")
        sys.exit(0)

    #Making the socket with the given port on localhost.

    HOST = "127.0.0.1" #localhost

    #If the user presses ctrl+c, the server and all clients will close
    signal.signal(signal.SIGINT, handler)
    atexit.register(endserver)
    
    #Creating the socket and making it reusable after the program closes
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.bind((HOST,PORT))
    serverSocket.listen()
    socketpid = []
    socketList = [serverSocket]
    clientNumber = 0
    maxClient = 4
    os.write(1,b"Server ouvert !\n")
    while True:
        #Waiting for a connection
        readable, _, _ = select.select(socketList,[],[])
        for s in readable:
            if s == serverSocket and clientNumber < maxClient:
                client, (HOSTC,PORTC) = serverSocket.accept()
                if HOSTC != HOST:
                    client.close()
                    continue
                #Creating a new process for each client and the client will be added to the list of clients 
                if sys.argv[1] == "cat": # Show if the second argument is a command "cat" or other
                    args = [sys.argv[1]]
                else:
                    args = [sys.argv[1],str(PORTC)] 
                socketList.append(client)
                clientNumber += 1
                pid = os.fork()        
                if pid == 0:
                    os.write(1,b"Client connecte avec le PID : "+str(os.getpid()).encode("utf-8")+b" et le port : "+str(PORTC).encode("utf-8")+b'\n')  
                    #Redirecting the stdin to the client and the stdout of the client
                    fd_in = client.fileno()
                    os.dup2(fd_in,1)
                    os.dup2(fd_in,0)
                    #Lauching the Traitant
                    os.execvp(args[0],args)
                socketpid.append([client,pid])
            elif s == serverSocket:
                pid, status = os.wait()
                socketpid = delPid(socketpid,1,pid)
                clientNumber -= 1
            else:
                clientNumber -= 1
                socketpid = delPid(socketpid,0,s)
                #If the client disconnects, the client will be removed from the list of clients
                socketList.remove(s)
                s.close()   
