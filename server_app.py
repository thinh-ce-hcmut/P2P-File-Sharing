import tkinter as tk
from server import Server
import threading
from tkinter import ttk


class Control_Page(tk.Frame):
    def __init__(self, parrent, app_controller):
        tk.Frame.__init__(self, parrent)

        self.app_controller = app_controller

        self.label_host = tk.Label(self, text="Input host name:")
        self.label_host.pack()

        self.label_ip = tk.Label(self, text="IP address:")
        self.label_ip.pack()

        self.host_ip = tk.StringVar(self)
        self.host_address = tk.StringVar(self)

        self.entry_host_name = tk.Entry(self, textvariable=self.host_ip)
        self.entry_host_name.pack()

        self.label_port = tk.Label(self, text="Port:")
        self.label_port.pack()

        self.entry_address = tk.Entry(self, textvariable=self.host_address)
        self.entry_address.pack()

        self.button_ping = tk.Button(self, text="Ping", command=self.ping)
        self.button_ping.pack()

        self.lable_notice = tk.Label(self, text="")
        self.lable_notice.pack()

        self.scroll = tk.Scrollbar(self)
        self.scroll.pack(side='right', fill='y')

        self.scroll = tk.Scrollbar(self, orient='horizontal')
        self.scroll.pack(side='bottom', fill='x')

        self.table = ttk.Treeview(
            self, yscrollcommand=self.scroll.set, xscrollcommand=self.scroll.set)
        self.table.pack()

        self.scroll.config(command=self.table.yview)
        self.scroll.config(command=self.table.xview)

        self.table['columns'] = ('File Name', 'Local Name')

        self.table.column("#0", width=0,  stretch=False)
        self.table.column("File Name", anchor="center", width=200)
        self.table.column("Local Name", anchor="center", width=200)

        self.table.heading("#0", text="", anchor="center")
        self.table.heading("File Name", text="File Name", anchor="center")
        self.table.heading("Local Name", text="Local Name", anchor="center")

        self.button_get = tk.Button(
            self, text="Discover", command=self.discover)
        self.button_get.pack()

    def ping(self):
        self.host = self.host_ip.get()
        self.host_ip.set("")

        self.port = self.host_address.get()
        self.host_address.set("")

        self.update_idletasks()

        try:
            self.port = int(self.port)
        except:
            self.lable_notice["text"] = "Not Found"
            self.update_idletasks()
            return

        ping = self.app_controller.server.ping((self.host, self.port))

        if ping:
            self.lable_notice["text"] = "Alive"
        else:
            self.lable_notice["text"] = "Not Found"
        self.update_idletasks()

    def discover(self):
        self.host = self.host_ip.get()
        self.host_ip.set("")

        self.port = self.host_address.get()
        self.host_address.set("")

        self.update_idletasks()

        try:
            self.port = int(self.port)
        except:
            self.lable_notice["text"] = "Not Found"
            self.update_idletasks()
            return

        lis = self.app_controller.server.discover((self.host, self.port))
        for row in self.table.get_children():
            self.table.delete(row)
        count = 0
        for file in lis:
            self.table.insert(
                parent='', index='end', iid={count}, text='', values=(file, lis[file]))
            count += 1
        self.lable_notice["text"] = ""
        self.update_idletasks()


class Server_App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.server = Server()

        self.title("File Sharing Server")
        self.geometry("500x500")

        self.container = tk.Frame()

        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        frame = Control_Page(self.container, self)
        frame.grid(row=0, column=0, sticky="nsew")

        frame.tkraise()

    def server_app_run(self):
        thread1 = threading.Thread(target=self.server.server_run)
        thread1.daemon = False
        thread1.start()

        self.mainloop()
        try:
            self.server.soc.close()
            self.server.status = False
        except:
            None


server_app = Server_App()
server_app.server_app_run()
