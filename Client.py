import socket
import threading

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

DISCONNECT_MESSAGE = "!DISCONNECT"
CONNECT_MESSAGE = "!CONNECT"
EXIT_COMMAND = "!EXIT"
COMMAND_PALLETE_TRIGGER = "COMMAND_PALLETE"

client = None
connected = False
receive_thread = None
send_thread = None
name = ""
command_mode = False


def send_name(sock):
    global name
    encoded_name = name.encode(FORMAT)
    name_length = len(encoded_name)
    send_length = str(name_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    sock.send(send_length)
    sock.send(encoded_name)


def send(sock):
    global connected, command_mode

    while connected:
        msg = input("Enter your message: ").strip()

        # Trigger command palette
        if msg == COMMAND_PALLETE_TRIGGER:
            command_mode = True
            print("\n=== COMMAND MODE ===")
            print("Available commands: !DISCONNECT | !EXIT")
            command = input("> ").strip().upper()

            if command == DISCONNECT_MESSAGE:
                try:
                    message = DISCONNECT_MESSAGE.encode(FORMAT)
                    msg_length = len(message)
                    send_length = str(msg_length).encode(FORMAT)
                    send_length += b' ' * (HEADER - len(send_length))
                    sock.send(send_length)
                    sock.send(message)
                except:
                    print("[ERROR] Could not send disconnect message.")
                connected = False
                sock.close()
                print("[INFO] Disconnected from chat.")
                break

            elif command == EXIT_COMMAND:
                try:
                    message = DISCONNECT_MESSAGE.encode(FORMAT)
                    msg_length = len(message)
                    send_length = str(msg_length).encode(FORMAT)
                    send_length += b' ' * (HEADER - len(send_length))
                    sock.send(send_length)
                    sock.send(message)
                    sock.close()
                except:
                    pass
                connected = False
                print("Goodbye!")
                exit()

            else:
                print("[INFO] Unknown command.")
            command_mode = False
            continue

        # Send regular message
        if not msg:
            continue
        message = msg.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        try:
            sock.send(send_length)
            sock.send(message)
        except:
            print("[ERROR] Message could not be sent.")
            break

        if msg == DISCONNECT_MESSAGE:
            connected = False
            sock.close()
            print("[INFO] Disconnected from chat.")
            break


def receive(sock):
    global connected
    while connected:
        try:
            msg = sock.recv(2048).decode(FORMAT)
            if msg:
                print(f"\n{msg}")
        except:
            if connected:
                print("[ERROR] Connection lost.")
            break


def start_chat(sock):
    global send_thread, receive_thread, connected
    connected = True
    send_thread = threading.Thread(target=send, args=(sock,))
    receive_thread = threading.Thread(target=receive, args=(sock,))
    receive_thread.start()
    send_thread.start()


def connect_to_chat():
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(ADDR)
        send_name(client)
        start_chat(client)
    except Exception as e:
        print(f"[ERROR] Could not connect: {e}")


# --- Initial launch ---
print("=== Welcome to the Chat App ===")
name = input("Enter your name: ")

# One-time command entry
print("\nAvailable commands: !CONNECT | !EXIT")
while True:
    command = input("> ").strip().upper()
    if command == CONNECT_MESSAGE and not connected:
        connect_to_chat()
        break
    elif command == EXIT_COMMAND:
        print("Goodbye!")
        exit()
    else:
        print("[INFO] Unknown or invalid command.")


