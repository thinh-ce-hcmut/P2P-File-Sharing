import socket
import json
import threading
import os
from tkinter.filedialog import asksaveasfilename

HOST = "127.0.0.1"
SERVER_PORT = 65432
FORMAT = "utf8"

MAX_CLIENTS = 3


class Client:
    def __init__(self):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.number_of_clients = 0

        print("CLIENT SIDE")
        self.status = self.init_connection()
        print("Server sends", self.status)
        if self.status:
            self.name = self.soc.getsockname()
            self.host = self.name[0]
            self.port = self.name[1]

            self.socket_client = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.socket_client.bind((self.host, self.port))
            self.socket_client.listen()

    def init_connection(self):
        try:
            self.soc.connect((HOST, SERVER_PORT))

            print("CLIENT", self.soc.getsockname())

            self.send_message("REQUEST CONNECTION")

            rec = self.receive_message()
            return rec
        except:
            return None

    def send_message(self, message):
        self.soc.sendall(message.encode(FORMAT))

    def receive_message(self):
        return self.soc.recv(1024).decode(FORMAT)

    def publish(self, file_name, local_name):
        self.send_message("SEND")

        rec = self.receive_message()
        print("Server sends", rec)

        if rec == "RESPONSE 200":
            file_package = {"file_name": file_name, "local_name": local_name}
            file_package = json.dumps(file_package)

            self.send_message(file_package)

            rec = self.receive_message()
            print("Server sends", rec)

            if rec == "RESPONSE 200":
                return True
            else:
                return False
        else:
            return False

    def request_file(self, file_name):
        self.send_message("REQUEST FILE")

        rec = self.receive_message()
        print("Server sends", rec)

        if rec == "RESPONSE 200":
            self.send_message(file_name)
            rec = self.receive_message()
            rec = json.loads(rec)
            if rec["availability"] == "yes":
                return rec["host_names"]
            else:
                return None

    def fetch(self, file_name):
        req = self.request_file(file_name)
        if req:
            for addr, local_file in req:
                if (addr[0], addr[1]) == self.soc.getsockname():
                    if os.path.exists(local_file):
                        return local_file
                else:
                    get = self.get_file(addr, local_file)
                if get:
                    return get
        return False

    def get_file(self, addr, local_file):
        socket_temp = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)

        try:
            socket_temp.connect((addr[0], addr[1]))

            socket_temp.sendall("FETCH".encode(FORMAT))
            rec = socket_temp.recv(1024).decode(FORMAT)

            print("client", addr, "sends", rec)
            if rec == "RESPONSE 200":
                socket_temp.sendall(local_file.encode(FORMAT))

                rec = socket_temp.recv(1024).decode(FORMAT)

                print("client", addr, "sends", rec)

                if rec != "RESPONSE 200":
                    return None

                size = socket_temp.recv(1024).decode(FORMAT)

                socket_temp.sendall("SEND".encode(FORMAT))

                data = b""
                for _ in range(int(size) // 1024 + 1):
                    try:
                        rec = socket_temp.recv(1024)
                        socket_temp.sendall("SEND".encode(FORMAT))
                        data += rec
                    except:
                        break

                files = [('All Files', '*.*')]
                file_name = asksaveasfilename(
                    filetypes=files, defaultextension=files)

                if not file_name:
                    directory = os.getcwd() + "\\file_sharing"

                    try:
                        os.mkdir(directory)
                    except:
                        None

                    file_name = directory + "\\" + local_file.split("/")[-1]
                file = open(file_name, "wb")

                file.write(data)
                file.close()

                socket_temp.close()

                return file_name

        except:
            return None

    def client_run(self):
        while self.status:
            try:
                conn, addr = self.socket_client.accept()

                thr = threading.Thread(
                    target=self.handle_client, args=(conn, addr))
                thr.daemon = False
                thr.start()

            except:
                break

    def handle_client(self, conn, addr):
        try:
            message = conn.recv(1024).decode(FORMAT)

            if message == "PING":
                print("SERVER want to ping")
                conn.sendall("RESPONSE 200".encode(FORMAT))
            elif message == "DISCOVER":
                print("SERVER want to discover")
                conn.sendall("RESPONSE 200".encode(FORMAT))

                dic = conn.recv(1024).decode(FORMAT)
                dic = self.discover(dic)

                conn.sendall(dic.encode(FORMAT))
            elif message == "FETCH":
                if self.number_of_clients < MAX_CLIENTS:
                    self.number_of_clients += 1
                    print("client:", addr, "sends", message)
                    conn.sendall("RESPONSE 200".encode(FORMAT))
                    self.send_file(conn, addr)
                    self.number_of_clients -= 1
                else:
                    conn.sendall("RESPONSE 404".encode(FORMAT))
        except:
            return

    def discover(self, dic):
        dic = json.loads(dic)
        temp_dic = {}
        for file_name in dic:
            if os.path.exists(dic[file_name]):
                temp_dic[file_name] = dic[file_name]
        return json.dumps(temp_dic)

    def send_file(self, conn, addr):
        local_file = conn.recv(1024).decode(FORMAT)

        if os.path.exists(local_file):
            conn.sendall("RESPONSE 200".encode(FORMAT))

            file = open(local_file, "rb")
            data = file.read()

            conn.sendall(str(len(data)).encode(FORMAT))

            conn.recv(1024).decode(FORMAT)

            for i in range(0, len(data), 1024):
                conn.sendall(data[i:i + 1024])
                conn.recv(1024).decode(FORMAT)

            file.close()
        else:
            conn.sendall("RESPONSE 404".encode(FORMAT))

    def get_list(self):
        try:
            self.send_message("GET LIST")

            rec = self.receive_message()
            print("Server sends", rec)

            if rec == "RESPONSE 200":
                self.send_message("SEND")

                lis = self.receive_message()
                return lis
        except:
            return None

    def get_my_file(self):
        try:
            self.send_message("GET MY FILE")

            rec = self.receive_message()
            print("Server sends", rec)

            if rec == "RESPONSE 200":
                self.send_message("SEND")

                lis = self.receive_message()
                return lis
        except:
            return None

    def delete_file(self, file_name):
        try:
            self.send_message("DELETE FILE")

            rec = self.receive_message()
            print("Server sends", rec)

            if rec == "RESPONSE 200":
                self.send_message(file_name)

                rec = self.receive_message()
                print("Server sends", rec)
        except:
            return None
