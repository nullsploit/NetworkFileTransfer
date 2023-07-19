from tkinter import filedialog as fd
from tkinter import *
import customtkinter
import socket
import os
import sys
import threading
from __main__ import Program


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def selectFile(app):
    files = fd.askopenfiles(initialdir = "/home")
    file_list = [file.name for file in files]

    if len(file_list) > 0:
        if len(Program.selected_files) > 0:
            for file in Program.selected_files:
                label = getattr(app, file)
                label.destroy()

        Program.selected_files = file_list
        Program.selected_folder = None
    
    for file in file_list:
        label = customtkinter.CTkLabel(app.scrollable_frame, text=f"{file.split('/')[-1]}", fg_color="transparent")
        label.pack(anchor=NW)
        setattr(app, file, label)


def selectFolder(app):
    foldername = fd.askdirectory(initialdir = "/home")
    Program.selected_files = []
    Program.selected_folder = foldername
    print(foldername)


def send_string(sock, string):
    sock.sendall(string.encode() + b'\n')

def send_int(sock, integer):
    sock.sendall(str(integer).encode() + b'\n')

def transmit(sock, folder):
    print(f'Sending folder: {folder}')
    send_string(sock, folder)
    files = os.listdir(folder)
    send_int(sock, len(files))
    for file in files:
        path = os.path.join(folder, file)
        filesize = os.path.getsize(path)
        print(f'Sending file: {file} ({filesize} bytes)')
        send_string(sock, file)
        send_int(sock, filesize)
        with open(path, 'rb') as f:
            sock.sendall(f.read())

def send_data(folder):
    s = socket.socket()
    s.connect(('localhost', 4563))
    with s:
        transmit(s, folder)


def start_discovery_server():
    Program.discovery_server_status = True
    discovery_server_thread = threading.Thread(target=discovery_server)
    discovery_server_thread.start()

def start_discovery_client(app):
    Program.discovery_server_status = True
    discovery_thread = threading.Thread(target=lambda:discovery_client(app))
    discovery_thread.start()



def discovery_client(app):
    network_ip = get_ip_address()
    print(f"IP: {network_ip}")

    while True:

        ip_prefix = ".".join(network_ip.split(".")[0:-1])
        for ip_suffix in range(253):
            ip_suffix +=1
            # print(f"checking '{ip_prefix}.{ip_suffix}'...")
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.1)
                    s.connect((f"{ip_prefix}.{ip_suffix}", 4562))

                    if f"{ip_prefix}.{ip_suffix}" not in Program.discovered_servers and not f"{ip_prefix}.{ip_suffix}" == network_ip:
                    # print(f"Found '{ip_prefix}.{ip_suffix}' is valid host")
                        Program.discovered_servers.append(f"{ip_prefix}.{ip_suffix}")

                        server_button = customtkinter.CTkButton(text=f"{ip_prefix}.{ip_suffix}", master=app.sidebar_frame)
                        server_button.grid(pady=4)
                        setattr(app.sidebar_frame, f"server-{ip_prefix}.{ip_suffix}", server_button)

                        s.sendall(b"conn-ping")
                        s.close()
            except:
                pass
                # if f"{ip_prefix}.{ip_suffix}" in Program.discovered_servers:
                #     button = getattr(app.sidebar_frame, f"server-{ip_prefix}.{ip_suffix}")
                #     button.destroy()
                #     Program.discovered_servers.remove(f"{ip_prefix}.{ip_suffix}")
                # s.sendall(b"Hello, world")
                # data = s.recv(1024)


def discovery_server():
    network_ip = get_ip_address()
    HOST = network_ip  # Standard loopback interface address (localhost)
    # HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
    PORT = 4562  # Port to listen on (non-privileged ports are > 1023)

    # network_ip = get_ip_address()
    # print(f"IP: {network_ip}")

    if not Program.discovery_server_status:
        print("Server not started")
        return
    else:
        print("Starting discovery server")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # ENABLE SOCKET REUSE
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 

        s.bind((HOST, PORT))
        s.listen()
        print("discovery server started")
        conn, addr = s.accept()
        with conn:
            # print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print("received", data)
                conn.sendall(data)


# def discovery_client():
#     HOST = "127.0.0.1"  # The server's hostname or IP address
#     PORT = 4562  # The port used by the server

#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         s.connect((HOST, PORT))
#         s.sendall(b"Hello, world")
#         data = s.recv(1024)

#     print(f"Received {data!r}")


def server():
    # if __name__ == '__main__':
    s = socket.socket()
    s.bind(('', 4563))
    s.listen()

    while True:
        client, address = s.accept()
        print(f'{address} connected')

        # client socket and makefile wrapper will be closed when with exits.
        with client, client.makefile('rb') as clientfile:
            while True:
                folder = clientfile.readline()
                if not folder:  # When client closes connection folder == b''
                    break
                folder = folder.strip().decode()
                no_files = int(clientfile.readline())
                print(f'Receiving folder: {folder} ({no_files} files)')
                # put in different directory in case server/client on same system
                folderpath = os.path.join('Downloads', folder)
                os.makedirs(folderpath, exist_ok=True)
                for i in range(no_files):
                    filename = clientfile.readline().strip().decode()
                    filesize = int(clientfile.readline())
                    data = clientfile.read(filesize)
                    print(f'Receiving file: {filename} ({filesize} bytes)')
                    with open(os.path.join(folderpath, filename), 'wb') as f:
                        f.write(data)



def upload():
    pass