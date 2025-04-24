import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
DISCONNECT_MESSAGE = "!DISCONNECT"
CLEAR_COMMAND = "cls"

class ChatClient:
    def __init__(self, root):
        self.client = None
        self.connected = False
        self.name = ""
        self.root = root
        self.root.config(bg="#3d3d3d")
        self.root.title("Chat App")
        self.root.resizable(False, False)
        
        # GUI setup
        button_style = {
            "bg": "#949393",
            "fg": "white",
            "activebackground": "white",
            "relief": "flat",    
            "font": ("Arial", 9, "bold"),
            "width": 8
        }

        chat_style = {
            "bg": "#d2d2d2",
            "fg": "black",
            "font": ("Arial", 8 ,"bold"),
        }

        entry_style = {
            "bg": "#949393",
            "fg": "white",
            "font": ("Arial", 10, "bold"),
            "relief": "flat"
        }

        self.chat_box = scrolledtext.ScrolledText(root, width=91, height=20, state='disabled', **chat_style)
        self.chat_box.pack(padx=10, pady=5)

        self.entry_field = tk.Entry(root, width=38, **entry_style)
        self.entry_field.pack(padx=10, pady=5, side=tk.LEFT)
        self.entry_field.bind("<Return>", self.send_msg_enter)


        self.send_button = tk.Button(root, text="Send", command=self.send_msg, **button_style)
        self.send_button.pack(padx=5, pady=5, side=tk.LEFT)

        self.connect_button = tk.Button(root, text="Connect", command=self.connect, **button_style)
        self.connect_button.pack(padx=5, pady=5, side=tk.LEFT)

        self.disconnect_button = tk.Button(root, text="Disconnect", command=self.disconnect, **button_style)
        self.disconnect_button.pack(padx=5, pady=5, side=tk.LEFT)

        self.clear_button = tk.Button(root, text="Clear", command=lambda: self.send_special(CLEAR_COMMAND),  **button_style)
        self.clear_button.pack(padx=5, pady=5, side=tk.LEFT)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def connect(self):
        if self.connected:
            self.write_chat("[INFO] Already connected.")
            return

        self.name = self.prompt_name()
        if not self.name:
            return

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect(ADDR)
            # Check if server is full
            try:
                self.client.settimeout(1.0)  # short timeout to read initial server response
                response = self.client.recv(1024).decode(FORMAT)
                if response == "SERVER_FULL":
                    self.write_chat("[INFO] Server is full. Try again later.")
                    self.client.close()
                    self.connected = False
                    return
            except socket.timeout:
                pass
            finally:
                self.client.settimeout(None)  # reset timeout
           
            self.send_name()
            self.connected = True
            threading.Thread(target=self.receive_msg, daemon=True).start()
            self.write_chat("[INFO] Connected to chat.")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to server:\n{e}")

    def prompt_name(self):
        return tk.simpledialog.askstring("Name", "Enter your name:")

    def send_name(self):
        name_encoded = self.name.encode(FORMAT)
        name_len = len(name_encoded)
        send_len = str(name_len).encode(FORMAT)
        send_len += b' ' * (HEADER - len(send_len))
        self.client.send(send_len)
        self.client.send(name_encoded)

    def send_msg(self):
        if not self.connected:
            self.write_chat("[INFO] Not connected.")
            return

        msg = self.entry_field.get().strip()
        if msg:
            try:
                encoded_msg = msg.encode(FORMAT)
                msg_len = len(encoded_msg)
                send_len = str(msg_len).encode(FORMAT)
                send_len += b' ' * (HEADER - len(send_len))
                self.client.send(send_len)
                self.client.send(encoded_msg)
                if msg == DISCONNECT_MESSAGE:
                    self.connected = False
                    self.client.close()
                    self.write_chat("[INFO] Disconnected.")
            except:
                self.write_chat("[ERROR] Failed to send message.")
            self.entry_field.delete(0, tk.END)

    def send_special(self, command):
        self.entry_field.delete(0, tk.END)
        self.entry_field.insert(0, command)
        self.send_msg()

    def receive_msg(self):
        while self.connected:
            try:
                msg = self.client.recv(2048).decode(FORMAT)
                if msg == "!CLEAR":
                    self.clear_chat()
                elif msg:
                    self.write_chat(msg)
            except:
                if self.connected:
                    self.write_chat("[ERROR] Connection lost.")
                    self.connected = False
                break

    def disconnect(self):
        if self.connected:
            self.send_special(DISCONNECT_MESSAGE)
        else:
            self.write_chat("[INFO] Not connected.")

    def write_chat(self, msg):
        self.chat_box.config(state='normal')
        self.chat_box.insert(tk.END, msg + "\n")
        self.chat_box.config(state='disabled')
        self.chat_box.yview(tk.END)
    
    def clear_chat(self):
        self.chat_box.config(state='normal')
        self.chat_box.delete('1.0', tk.END)
        self.chat_box.config(state="disabled")
    
    def send_msg_enter(self, event):
        self.send_msg()

    def on_closing(self):
        if self.connected:
            try:
                self.send_special(DISCONNECT_MESSAGE)
            except:
                pass
        self.root.destroy()

# === Start GUI ===
if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClient(root)
    root.mainloop()
