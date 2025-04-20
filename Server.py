import socket
import threading
from datetime import datetime

# header size for messages 8 bytes
HEADER = 64
# port number for the server
PORT = 5050
# server address local IP address
SERVER = socket.gethostbyname(socket.gethostname())
# connecting to the server with the port number and address
ADDR = (SERVER, PORT)
# encoding format for the messages
FORMAT = 'utf-8'
# disconnect message to close the connection
DISCONNECT_MESSAGE = "!DISCONNECT"
# command to clear the chat history
CLEAR_COMMAND = "cls"  
# IPv4 address family and TCP socket type
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# binding the server to the address and port
server.bind(ADDR)


# lists and dictionaries to manage clients and chat history
clients = []
names = {}
chat_history = []
# locks for thread safety
lock = threading.Lock()
cout_lock = threading.Lock()

# sending messages to all clients and checking for disconnections
def broadcast(msg, sender_conn=None):
    with lock:
        for client in clients.copy():
                try:
                    client.send(msg.encode(FORMAT))
                except:
                
                    try:
                        clients.remove(client)
                        if client in names:
                            del names[client]
                    except:
                        pass

# function to handle client connections
def handle_client(conn, addr):
    with cout_lock:
        print(f"[NEW CONNECTION] {addr} connected.")

    with lock:
        # add the new client to the list of clients
        clients.append(conn)
 
    try:
        # receive the name of the client
        name_length = int(conn.recv(HEADER).decode(FORMAT))
        name = conn.recv(name_length).decode(FORMAT)
        with lock:
            names[conn] = name

        # send the chat history to the new client
        with lock:
            history_text = "\n".join(chat_history)
        if history_text:
            try:
                conn.send(history_text.encode(FORMAT))
            except:
                pass

    except:
        # if there was an error receiving the name, close the connection
        with lock:
            if conn in clients:
                clients.remove(conn)
            if conn in names:
                del names[conn]
        conn.close()
        return

    # send a message to all clients that a new user has joined
    connected = True
    while connected:
        try:
            # receive the message length and the message itself
            msg_length = conn.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(FORMAT)

                # check if the message is a disconnect message or a clear command
                if msg == DISCONNECT_MESSAGE:
                    connected = False

                elif msg == CLEAR_COMMAND:
                    with lock:
                        chat_history.clear()
                    broadcast("!CLEAR")
                    broadcast("[SERVER]: Chat history has been cleared by a user.")
                    with cout_lock:
                        print(f"[{addr}] {name} cleared chat history.")

                else:
                    # get the current time and format the message
                    time_sent = datetime.now().strftime("%H:%M:%S")
                    with lock:
                        # get the sender's name from the names dictionary
                        sender_name = names.get(conn, "Unknown")
                    #  format the message with the time and sender's name
                    formatted_msg = f"{time_sent} {sender_name}: {msg}"

                    with lock:
                        # add the message to the chat history
                        chat_history.append(formatted_msg)
                    with cout_lock:
                        print(f"[{addr}] {formatted_msg}")
                        # send the message to all clients
                    broadcast(formatted_msg, conn)

        except:
            break

    with lock:
        # close the connection and remove the client from the list
        if conn in clients:
            clients.remove(conn)
        if conn in names:
            # remove the client from the names dictionary
            del names[conn]

    conn.close()
    with cout_lock:
        print(f"[DISCONNECTED] {addr} disconnected.")

# function to start the server and listen for incoming connections
def start():
    # start the server and listen for incoming connections
    server.listen()
    with cout_lock:
        print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        # accept incoming connections
        conn, addr = server.accept()
        # create a new thread for each client connection
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        # start the thread 
        thread.start()
        with cout_lock:
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

with cout_lock:
    print("[STARTING] Server is starting...")

# start the server
start()
