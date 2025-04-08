import socket
import threading

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_client.connect(ADDR)

# Funkcja do wysyłania wiadomości
def send():
    while True:
        msg = input()
        message = msg.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        socket_client.send(send_length)
        socket_client.send(message)
        if msg == DISCONNECT_MESSAGE:
            break
    socket_client.close()

# Funkcja do odbierania wiadomości
def receive():
    while True:
        try:
            msg = socket_client.recv(2048).decode(FORMAT)
            if msg:
                print(f"\n[SERVER]: {msg}")
        except:
            print("[ERROR] Connection closed or failed.")
            break

# Uruchomienie dwóch wątków
receive_thread = threading.Thread(target=receive)
send_thread = threading.Thread(target=send)

receive_thread.start()
send_thread.start()
