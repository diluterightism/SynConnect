# UNITED HACKS PROJECT - SynConnect
The development process for SynConnect

voice_chat_client.py and voice_chat_server.py are the applications.
everything else is for the website.

### REQUIRED PACKAGES
* PyQt5 (install using `pip install pyqt5`)
* threading (inbuilt)
* socket (inbuilt)
* pyaudio (install using `pip install pyaudio`)

<hr>

### HOW TO RUN APPLICATION

1. Note down the ip address of the system that you wish to run your server on
2. Make sure that ports 5000 and 5001 are open for use
3. Replace the HOST variable in voice_chat_server.py with the ip address of the server.
4. Run voice_chat_server.py using the cmd `python voice_chat_server.py`
5. When the app pops up, click on **Start Connecting**. 
6. In the other system, where you wish to connect from, replace HOST variable in voice_chat_client.py with ip addr of server.
7. Run voice_chat_client.py using the cmd `python voice_chat_client.py`
8. In the client app, click on the Voice Call button in the horizontal navbar
9. Finally, click **Connect** to establish connection with the server. The status label should now show **Connected**

