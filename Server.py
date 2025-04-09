import socket
import threading
from datetime import datetime

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
CLEAR_COMMAND = "cls"  # Komenda do czyszczenia historii

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = []
names = {}
chat_history = []  # Historia czatu
lock = threading.Lock()
cout_lock = threading.Lock()

def broadcast(msg, sender_conn=None):
    with lock:
        for client in clients.copy():
            try:
                client.send(msg.encode(FORMAT))
            except:
                clients.remove(client)
                if client in names:
                    del names[client]

def handle_client(conn, addr):
    with cout_lock:
        print(f"[NEW CONNECTION] {addr} connected.")

    with lock:
        clients.append(conn)

    try:
        name_length = int(conn.recv(HEADER).decode(FORMAT))
        name = conn.recv(name_length).decode(FORMAT)
        with lock:
            names[conn] = name

        # Wyślij historię czatu do nowego klienta
        with lock:
            for msg in chat_history:
                try:
                    conn.send(msg.encode(FORMAT))
                except:
                    pass

    except:
        with lock:
            if conn in clients:
                clients.remove(conn)
        conn.close()
        return

    connected = True
    while connected:
        try:
            msg_length = conn.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(FORMAT)

                if msg == DISCONNECT_MESSAGE:
                    connected = False
                elif msg == CLEAR_COMMAND:
                    # Czyszczenie historii
                    with lock:
                        chat_history.clear()
                    broadcast("[SERVER]: Chat history has been cleared by a user.")
                    with cout_lock:
                        print(f"[{addr}] {name} cleared chat history.")
                else:
                    time_sent = datetime.now().strftime("%H:%M:%S")
                    with lock:
                        sender_name = names.get(conn, "Unknown")
                    formatted_msg = f"{time_sent} {sender_name}: {msg}"

                    with lock:
                        chat_history.append(formatted_msg)  # Zapisz do historii
                    with cout_lock:
                        print(f"[{addr}] {formatted_msg}")
                    broadcast(formatted_msg, conn)
        except:
            break

    with lock:
        if conn in clients:
            clients.remove(conn)
        if conn in names:
            del names[conn]

    conn.close()
    with cout_lock:
        print(f"[DISCONNECTED] {addr} disconnected.")

def start():
    server.listen()
    with cout_lock:
        print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        with cout_lock:
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

with cout_lock:
    print("[STARTING] Server is starting...")

start()
