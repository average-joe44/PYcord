# PYcord
## What is it
PYcord is a Discord RAT that uses C2 concept and post-exploitation techniques.
## Features
PYcord featuring multiple cool commands you can use to control your targets, including:
```
.help  to show help
.cd    to change directory
.ls    to list directory
.exe <command> to run windows command
.rmv <file> to delete a file
.size <file> to calculate file size
.who to show current user and machine
.addstartup to add file to startup
.recordmic <seconds> to record mic for
.stoprecord to stop mic recording early
.screenshare <url> to screen share from client to you through tunnel
.stopsharing to stop screen sharing

.hello to make sure if bot is running
.marco to show latency

.screenshot to screen shot
.snapcam  to snap camera

.keylog_start to start keylogger
.keylog_read to read keylogger
.keylog_stop to stop keylogger

.cliplog_start to start cliplogger
.cliplog_read to read cliplogger
.cliplog_stop to stop cliplogger

.download <file> to make file from target into downloadable link
.upload <url-with-file> to make file from a url uploaded into target
```
## NOTE
In order to run screenshare function you'd have to install a tunneling service in your computer!!!  
And before you run the screenshare function, you have to run the serverScreenHolder first and bind it with your ngrok port.
