import customtkinter
import threading

class Program:
    selected_files = []
    selected_folder = None
    discovery_server_status = False
    discovered_servers = []

from func import *



customtkinter.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        # self.title("CustomTkinter complex_example.py")
        self.title("Network File transfer")
        self.geometry(f"700x400")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        self.resizable(False, False) 

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.scrollable_frame = customtkinter.CTkScrollableFrame(self, width=500, height=300)
        self.scrollable_frame.grid(column=1, row=0, columnspan=3)

        self.file_button = customtkinter.CTkButton(text="Select File(s)", command=lambda:selectFile(self), master=self.sidebar_frame)
        self.file_button.grid(pady=4)

        self.folder_button = customtkinter.CTkButton(text="Select Folder", command=lambda:selectFolder(self), master=self.sidebar_frame)
        self.folder_button.grid(pady=4)

        label = customtkinter.CTkLabel(self.sidebar_frame, text="Servers", fg_color="transparent")
        label.grid(pady=4)

        # self.discovery_server_button = customtkinter.CTkButton(text=f"Start Server", command=start_discovery_server, master=self.sidebar_frame)
        # self.discovery_server_button.grid(pady=4)

        self.send_button = customtkinter.CTkButton(text="Send", command=upload, master=self)
        self.send_button.grid(padx=4, pady=4, column=1, row=1)


        start_discovery_server()
        start_discovery_client(self)
        

        self.mainloop()


if __name__ == "__main__":
    app = App()
    app.mainloop()