import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog 

# header size for messages 8 bytes
HEADER = 64
# port number for the server
PORT = 5050
# format for the messages
FORMAT = 'utf-8'
# server address local IP address
SERVER = socket.gethostbyname(socket.gethostname())
# connecting to the server with the port number and address
ADDR = (SERVER, PORT)
# disconnect message to close the connection
DISCONNECT_MESSAGE = "!DISCONNECT"
# command to clear the chat history
CLEAR_COMMAND = "cls"

# class for the chat client GUI
# This class handles the GUI for the chat client, including sending and receiving messages.
class ChatClient:
    def __init__(self, root):
        # Initialize the client and GUI components
        self.client = None
        self.connected = False
        self.name = ""
        self.root = root
        self.root.title("Chat App")
        
        # GUI setup
        # Create a scrolled text box for chat messages
        self.chat_box = scrolledtext.ScrolledText(root, width=60, height=20, state='disabled')
        self.chat_box.pack(padx=10, pady=5)

        # Create an entry field for user input
        self.entry_field = tk.Entry(root, width=50)
        self.entry_field.pack(padx=10, pady=5, side=tk.LEFT)

        # Create buttons for sending messages and connecting/disconnecting
        self.send_button = tk.Button(root, text="Send", command=self.send_msg)
        self.send_button.pack(padx=5, pady=5, side=tk.LEFT)

        self.connect_button = tk.Button(root, text="!CONNECT", command=self.connect)
        self.connect_button.pack(padx=5, pady=5, side=tk.LEFT)

        self.disconnect_button = tk.Button(root, text="!DISCONNECT", command=self.disconnect)
        self.disconnect_button.pack(padx=5, pady=5, side=tk.LEFT)

        self.clear_button = tk.Button(root, text="cls", command=lambda: self.send_special(CLEAR_COMMAND))
        self.clear_button.pack(padx=5, pady=5, side=tk.LEFT)

        # Bind the Enter key to send messages
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    # Connect to the server and handle user input
    def connect(self):
        if self.connected:
            self.write_chat("[INFO] Already connected.")
            return

        # Prompt for the user's name
        self.name = self.prompt_name()
        if not self.name:
            return

        # Create a socket and connect to the server
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Connect to the server
            self.client.connect(ADDR)
            # Send the name to the server
            self.send_name()
            self.connected = True
            # Start a thread to receive messages from the server
            threading.Thread(target=self.receive_msg, daemon=True).start()
            self.write_chat("[INFO] Connected to chat.")
        except Exception as e:
            # If there is an error connecting to the server, show an error message
            messagebox.showerror("Connection Error", f"Could not connect to server:\n{e}")

    # Prompt for the user's name
    def prompt_name(self):
        # Prompt the user for their name using a simple dialog box
        return tk.simpledialog.askstring("Name", "Enter your name:")

    # Send the user's name to the server
    def send_name(self):
        name_encoded = self.name.encode(FORMAT)
        name_len = len(name_encoded)
        send_len = str(name_len).encode(FORMAT)
        # Pad the length to fit the header size
        send_len += b' ' * (HEADER - len(send_len))
        # Send the length and name to the server
        self.client.send(send_len)
        self.client.send(name_encoded)

    # Send a message to the server
    def send_msg(self):
        if not self.connected:
            self.write_chat("[INFO] Not connected.")
            return

        # Get the message from the entry field and encode it
        msg = self.entry_field.get().strip()
        if msg:
            try:
                # Encode the message and send it to the server
                encoded_msg = msg.encode(FORMAT)
                msg_len = len(encoded_msg)
                send_len = str(msg_len).encode(FORMAT)
                # Pad the length to fit the header size
                send_len += b' ' * (HEADER - len(send_len))
                self.client.send(send_len)
                self.client.send(encoded_msg)
                # If the message is a disconnect command, close the connection
                if msg == DISCONNECT_MESSAGE:
                    self.connected = False
                    # Close the client socket
                    self.client.close()
                    # Notify the user that the connection is closed
                    self.write_chat("[INFO] Disconnected.")
            except:
                self.write_chat("[ERROR] Failed to send message.")
            # Clear the entry field after sending the message
            self.entry_field.delete(0, tk.END)

    # Send a special command to the server (e.g., clear chat history)
    def send_special(self, command):
        # If the client is not connected, show an error message
        self.entry_field.delete(0, tk.END)
        # If the command is to clear the chat history, send the command to the server
        self.entry_field.insert(0, command)
        # Send the command to the server
        self.send_msg()

    # Receive messages from the server
    def receive_msg(self):
        # Continuously listen for messages from the server
        while self.connected:
            try:
                # Receive the message from the server
                msg = self.client.recv(2048).decode(FORMAT)
                if msg:
                    self.write_chat(msg)
            except:
                if self.connected:
                    self.write_chat("[ERROR] Connection lost.")
                break

    # Disconnect from the server
    def disconnect(self):
        if self.connected:
            # If the client is connected, send a disconnect message to the server
            self.send_special(DISCONNECT_MESSAGE)
        else:
            # If the client is not connected, show an error message
            self.write_chat("[INFO] Not connected.")

    # Write a message to the chat box
    # This function updates the chat box with the received message.
    def write_chat(self, msg):
        self.chat_box.config(state='normal')
        self.chat_box.insert(tk.END, msg + "\n")
        self.chat_box.config(state='disabled')
        self.chat_box.yview(tk.END)

    ## Handle the window closing event
    def on_closing(self):
        if self.connected:
            try:
                # If the client is connected, send a disconnect message to the server
                self.send_special(DISCONNECT_MESSAGE)
            except:
                pass
        # Close the client socket
        self.root.destroy()

# Start GUI 
if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClient(root)
    root.mainloop()
