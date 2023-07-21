from tkinter import filedialog as fd
from tkinter import *
import customtkinter
import socket
import os
import sys
import threading
from __main__ import Program


def is_windows():
    if os.name == 'nt':
        return True
    else:
        return False


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def selectFile(app):
    if is_windows():
        files = fd.askopenfiles(initialdir = "c:\\")
    else:
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
        label = customtkinter.CTkLabel(app.scrollable_frame, text=f"{file.split(Program.slash_seperator)[-1]}", fg_color="transparent")
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

def transmit(sock, folder, files):
    print(f'Sending folder: {folder}')
    send_string(sock, folder)
    # files = os.listdir(folder)
    send_int(sock, len(files))
    for file in files:
        filename = file.split(Program.slash_seperator)[-1]
        # path = os.path.join(folder, file)
        path = file
        filesize = os.path.getsize(path)
        print(f'Sending file: {filename} ({filesize} bytes)')
        send_string(sock, file)
        send_int(sock, filesize)
        with open(path, 'rb') as f:
            sock.sendall(f.read())

def send_data():
    s = socket.socket()
    s.connect((Program.selected_server, 4563))
    with s:
        transmit(s, "Data", Program.selected_files)


def start_discovery_server(app):
    Program.discovery_server_status = True
    discovery_server_thread = threading.Thread(target=lambda:discovery_server(app))
    discovery_server_thread.start()

def start_discovery_client(app):
    discovery_thread = threading.Thread(target=lambda:discovery_client(app))
    discovery_thread.start()

def start_transfer_server():
    discovery_thread = threading.Thread(target=server)
    discovery_thread.start()



def discovery_client(app):
    network_ip = get_ip_address()
    # print(f"IP: {network_ip}")
    print("Finding servers...")


    ip_prefix = ".".join(network_ip.split(".")[0:-1])
    for ip_suffix in range(253):
        ip_suffix +=1

        full_ip = f"{ip_prefix}.{ip_suffix}"
        # print(f"checking '{ip_prefix}.{ip_suffix}'...")
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)
                s.connect((f"{full_ip}", 4562))

                if f"{full_ip}" not in Program.discovered_servers and not f"{full_ip}" == network_ip:
                    print(f"Found '{ip_prefix}.{ip_suffix}' is valid host")
                    Program.discovered_servers.append(f"{full_ip}")

                    server_button = customtkinter.CTkButton(text=full_ip, command=lambda:select_server(full_ip), master=app.sidebar_frame)
                    server_button.grid(pady=4)
                    setattr(app.sidebar_frame, f"server-{full_ip}", server_button)

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
    print("Stopped finding servers")


def discovery_server(app):
    network_ip = get_ip_address()
    HOST = network_ip  # Standard loopback interface address (localhost)
    # HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
    PORT = 4562  # Port to listen on (non-privileged ports are > 1023)

    # network_ip = get_ip_address()
    # print(f"IP: {network_ip}")
    # try:
    #     discovery_button = getattr(app, "discovery_button")
    #     discovery_button.destroy()
    # except:
    #     pass

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
        Program.discovery_server_status = False
        print("Stopped discovery server")
        
        start_discovery_server(app)
        # discovery_button = customtkinter.CTkButton(text="Start Discovery", command=lambda:start_discovery_server(app), master=app.sidebar_frame)
        # setattr(app, "discovery_button", discovery_button)
        # app.discovery_button.grid(pady=4)

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


def select_server(server_ip):
    Program.selected_server = server_ip
    print(f"Selected '{server_ip}' as server")


def upload(app):
    if not Program.selected_server:
        return

    setattr(app, "progressbar", customtkinter.CTkProgressBar(app))
    app.progressbar.grid(padx=0, pady=4, column=1, row=2, columnspan=3)
    app.progressbar.configure(mode="indeterminnate")
    app.progressbar.start()

    dummy_val = 2

    send_data()

    progress_bar = getattr(app, "progressbar")
    progress_bar.destroy()



    # server_ip = Program.selected_server

    