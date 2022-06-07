# WebShell

![](https://iconarchive.com/download/i99290/froyoshark/enkel/iTerm.ico)

## Instructions

**To launch the webShell, simply run the following command:**
```sh
chmod u+x *
./server.py ./traitantx.py PORT
```
You can use another "traitant" by changing ./traitantx.py with the wanted file.
The port must be between 1024 and 65535

PS : 
- Commands works only webshellx.py. 
- webshell_final.py is fully operational
- webshell3.py is fully operational but without UI


## Added Features

- Intuitive User Interface
- You can use arrow up and down to navigate history
- `clear` command works without clearing navigate history
- `cd` command works thanks to fifo stored in /tmp/FIFO\*
- `read` command works, use it to store the next entry into $REPLY var
- .txt saves are stored in /tmp/logs_XXXXX.txt
- `webshell_final.py` use .json save with this scheme :

```json
token{
"commands":["",""],
"history":["",""]
}
```
- Ctrl+C the server will kill all clients properly and deletes created files
- Server doesn't accept more than 4 connections

# Demo

![](https://s8.gifyu.com/images/webshell.gif)
