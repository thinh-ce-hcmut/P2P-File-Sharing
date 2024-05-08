import tkinter as tk
from tkinter import messagebox
from client import Client
from tkinter.filedialog import askopenfile
import threading
from tkinter import ttk
import json


class Dead_Page(tk.Frame):
    def __init__(self, parrent, app_controller):
        tk.Frame.__init__(self, parrent)

        self.label_notice = tk.Label(self, text="Server is dead")
        self.label_notice.pack()


class Start_Page(tk.Frame):
    def __init__(self, parrent, app_controller):
        tk.Frame.__init__(self, parrent)

        self.label_welcome = tk.Label(
            self, text="Torrent File Sharing App", fg="white", bg="blue", font=("Times New Roman", 18), background="blue")
        self.label_welcome.pack(fill=tk.X)

        # self.label_option = tk.Label(self, text="Choose your option:")
        # self.label_option.pack(fill=tk.X)

        self.button_share = tk.Button(
            self, text="Share your file", command=lambda: app_controller.show_page(Share_Page), bd='5')
        self.button_share.pack(fill=tk.X)

        self.button_mine = tk.Button(
            self, text="Get my published file", command=lambda: app_controller.show_page(List_Mine_Page), bd='5')
        self.button_mine.pack(fill=tk.X)

        self.button_mine = tk.Button(
            self, text="Download file", command=lambda: app_controller.show_page(Combine_Page), bd='5')
        self.button_mine.pack(fill=tk.X)


class Share_Page(tk.Frame):
    def __init__(self, parrent, app_controller):
        tk.Frame.__init__(self, parrent)

        self.app_controller = app_controller

        self.button_back = tk.Button(
            self, text="Back", command=lambda: app_controller.show_page(Start_Page), bd="5")
        self.button_back.grid(row=0, column=0, sticky="ew")
        self.grid_columnconfigure([0, 1], weight=1)
        self.label_work = tk.Label(
            self, text="Choose your file:")
        self.label_work.grid(row=1, column=0, sticky="ew")

        self.button_choose = tk.Button(
            self, text="Select file", command=self.select_file, bd='5')
        self.button_choose.grid(row=1, column=1, sticky="ew")

        self.label_choose = tk.Label(
            self, text="Input your file name:")
        self.label_choose.grid(row=2, column=0, sticky="ew")

        self.entry_local_name_var = tk.StringVar()

        self.entry_local_name = tk.Entry(
            self, textvariable=self.entry_local_name_var)
        self.entry_local_name.grid(row=2, column=1, sticky="ew")

        self.button_publish = tk.Button(
            self, text="Publish", command=self.publish, bd='5')
        self.button_publish.grid(row=0, column=1, sticky="ew")

        self.label_file = tk.Label(self, text="")
        self.label_file.grid(row=3, column=0, sticky="ew")

    def select_file(self):
        self.file = askopenfile()

        messagebox.showinfo(
            "Information", "Your selected file is " + self.file.name)
        self.update_idletasks()

    def publish(self):
        try:
            local_name = self.file.name
            self.file = None
        except:
            self.update_idletasks()
            messagebox.showwarning("Warning", "You have to select file")

            return
        file_name = self.entry_local_name_var.get()

        if "." in local_name:
            post_fix_local = local_name.split(".")[-1]
            if not "." in file_name:
                self.update_idletasks()
                messagebox.showwarning(
                    "Warning", "Your file's name has to be *." + post_fix_local)

                return
            post_fix_file = file_name.split(".")[-1]
            if post_fix_file != post_fix_local:
                self.update_idletasks()
                messagebox.showwarning(
                    "Warning", "Your file's name has to be *." + post_fix_local)

                return

        self.label_file["text"] = "Waiting to publish"
        self.entry_local_name_var.set("")
        self.update_idletasks()

        pub = self.app_controller.client.publish(file_name, local_name)
        if pub:
            self.label_file["text"] = ""
            self.update_idletasks()
            messagebox.showinfo(
                "Information", "Publish sucessfully, share new file")
        else:
            self.label_file["text"] = ""
            self.update_idletasks()
            messagebox.showerror(
                "Information", "Publish failed, share new file")


class Download_Page(tk.Frame):
    def __init__(self, parrent, app_controller):
        tk.Frame.__init__(self, parrent)

        self.app_controller = app_controller
        self.grid_columnconfigure([0, 1], weight=1)

        self.button_back = tk.Button(
            self, text="Back", command=lambda: app_controller.show_page(Start_Page), bd='5')
        self.button_back.grid(row=0, column=0, sticky="ew")

        self.label_work = tk.Label(self, text="Input name file to download:")
        self.label_work.grid(row=1, column=0, sticky="ew")

        self.entry_file_name_var = tk.StringVar()

        self.entry_file_name = tk.Entry(
            self, textvariable=self.entry_file_name_var)
        self.entry_file_name.grid(row=1, column=1, sticky="ew")

        self.button_get = tk.Button(
            self, text="Download", command=self.download_file, bd='5')
        self.button_get.grid(row=0, column=1, sticky="ew")

        self.label_notice = tk.Label(self, text="")
        self.label_notice.grid(row=2, column=0, sticky="ew")

    def download_file(self):
        file_name = self.entry_file_name_var.get()
        self.entry_file_name_var.set("")

        if file_name == "":
            return

        self.label_notice["text"] = "Downloading " + file_name + "..."
        self.update_idletasks()

        get = self.app_controller.client.fetch(file_name)

        if get:
            self.label_notice["text"] = ""
            self.update_idletasks()
            messagebox.showinfo(
                "Information", "Your file in " + get + ", download new file")
        else:
            self.label_notice["text"] = ""
            self.update_idletasks()
            messagebox.showerror("Error", "Download failed, download new file")


class List_Page(tk.Frame):
    def __init__(self, parrent, app_controller):
        tk.Frame.__init__(self, parrent)

        self.app_controller = app_controller

        self.scroll = tk.Scrollbar(self)
        self.scroll.pack(side='right', fill='y')

        self.scroll = tk.Scrollbar(self, orient='horizontal')
        self.scroll.pack(side='bottom', fill='x')

        self.table = ttk.Treeview(
            self, yscrollcommand=self.scroll.set, xscrollcommand=self.scroll.set)
        self.table.pack(fill=tk.X)

        self.scroll.config(command=self.table.yview)
        self.scroll.config(command=self.table.xview)

        self.table['columns'] = ('File Name', 'Host Name')

        self.table.column("#0", width=0,  stretch=False)
        self.table.column("File Name", anchor="center", width=200)
        self.table.column("Host Name", anchor="center", width=200)

        self.table.heading("#0", text="", anchor="center")
        self.table.heading("File Name", text="File Name", anchor="center")
        self.table.heading(
            "Host Name", text="Number of owners", anchor="center")

        self.button_get = tk.Button(
            self, text="Get list", command=self.get_list, bd='5')
        self.button_get.pack(fill=tk.X)

    def get_list(self):
        for row in self.table.get_children():
            self.table.delete(row)

        lis = self.app_controller.client.get_list()
        lis = json.loads(lis)

        count = 0
        for file in lis:
            self.table.insert(
                parent='', index='end', iid={count}, text='', values=(file, len(lis[file])))
            count += 1

        self.update_idletasks()


class List_Mine_Page(tk.Frame):
    def __init__(self, parrent, app_controller):
        tk.Frame.__init__(self, parrent)

        self.app_controller = app_controller
        self.data = []

        self.button_back = tk.Button(
            self, text="Back", command=lambda: app_controller.show_page(Start_Page), bd='5')
        self.button_back.grid(row=0, column=0, sticky="ew")

        self.button_get = tk.Button(
            self, text="Update my list", command=lambda: self.get_my_file(), bd='5')
        self.button_get.grid(row=0, column=1, sticky="ew")
        self.grid_columnconfigure([0, 1], weight=1)
        tk.Label(self, text="File Name", anchor="center", justify='center').grid(
            row=2, column=0, sticky="ew")
        tk.Label(self, text="Action", anchor="center", justify='center').grid(
            row=2, column=1, sticky="ew")

    def get_my_file(self):
        for label, button in self.data:
            label.grid_forget()
            button.grid_forget()
        self.data = []
        row = 3
        lis = self.app_controller.client.get_my_file()
        lis = json.loads(lis)

        for file_name in lis:
            file_label = tk.Label(self, text=file_name, anchor="center")
            file_label = tk.Label(self, text=file_name, anchor="center")
            action_button = tk.Button(
                self, text="Delete", command=lambda file_name=file_name: self.delete_file(file_name), bd='5')
            self.data.append((file_label, action_button))

            file_label.grid(row=row, column=0, sticky="ew")
            action_button.grid(row=row, column=1)

            row += 1

        self.update_idletasks()

    def delete_file(self, file_name):
        self.app_controller.client.delete_file(file_name)
        self.get_my_file()


class Combine_Page(tk.Frame):
    def __init__(self, parrent, app_controller):
        tk.Frame.__init__(self, parrent)

        self.grid_columnconfigure([0], weight=1)

        block1 = Download_Page(self, app_controller)
        block1.grid(row=0, column=0, sticky="nsew", padx=(5, 5))

        block2 = List_Page(self, app_controller)
        block2.grid(row=1, column=0, sticky="nsew", padx=(5, 5))


class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.client = Client()

        self.title("File Sharing Application")
        self.geometry("400x340")

        self.container = tk.Frame()

        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for f in {Dead_Page, Start_Page, Share_Page, Combine_Page, List_Mine_Page}:
            frame = f(self.container, self)
            frame.grid(row=0, column=0, sticky="nsew")
            self.frames[f] = frame
        if self.client.status:
            self.frames[Start_Page].tkraise()
        else:
            self.frames[Dead_Page].tkraise()

    def show_page(self, frame):
        self.frames[frame].tkraise()

    def __del__(self):
        try:
            self.client.send_message("END")
            self.client.soc.close()
        except:
            None

    def app_run(self):
        thread1 = threading.Thread(target=self.client.client_run)
        thread1.daemon = False
        thread1.start()

        self.mainloop()
        try:
            self.client.socket_client.close()
            self.client.status = False
        except:
            None


app = App()
app.app_run()
