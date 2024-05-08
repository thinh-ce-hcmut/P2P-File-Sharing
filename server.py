import socket
import threading
import json

HOST = "127.0.0.1"
SERVER_PORT = 65432
FORMAT = "utf8"


print("SERVER SIDE")
print("server:", HOST, SERVER_PORT)
print("Waiting for Clients")


class Server:
    def __init__(self):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.status = True

        self.soc.bind((HOST, SERVER_PORT))
        self.soc.listen()

        self.clients = {}
        self.file_names = {}

    def server_run(self):
        while self.status:
            if len(self.clients) >= 5:
                continue
            try:
                conn, addr = self.soc.accept()

                thr = threading.Thread(
                    target=self.handle_client, args=(conn, addr))
                thr.daemon = False
                thr.start()

            except:
                break

    def handle_client(self, conn, addr):
        print("client address:", addr)
        print("conn:", conn.getsockname())

        accept = self.accept_connection(conn, addr)

        while accept:
            try:
                end = self.receive_message(conn, addr)
            except:
                self.clients.pop(addr, None)
                break
            if end:
                self.clients.pop(addr, None)
                break
        print("client", addr, "finished")
        print(conn.getsockname(), "closed")
        conn.close()

    def accept_connection(self, conn, addr):
        rec = conn.recv(1024).decode(FORMAT)
        print("client:", addr, "sends", rec)
        if rec == "REQUEST CONNECTION":
            self.clients[addr] = {}
            conn.sendall("RESPONSE 200".encode(FORMAT))
            return True
        else:
            conn.sendall("RESPONSE 404".encode(FORMAT))
            return False

    def receive_message(self, conn, addr):
        try:
            message = conn.recv(1024).decode(FORMAT)
            print("client:", addr, "sends", message)
            if message == "END":
                return True
            elif message == "SEND":
                end = self.publish(conn, addr)
            elif message == "REQUEST FILE":
                end = self.send_list_clients(conn, addr)
            elif message == "GET LIST":
                end = self.send_list(conn, addr)
            elif message == "GET MY FILE":
                end = self.send_my_file(conn, addr)
            elif message == "DELETE FILE":
                end = self.delete_file(conn, addr)
            return end
        except:
            return True

    def publish(self, conn, addr):
        try:
            conn.sendall("RESPONSE 200".encode(FORMAT))
        except:
            return True
        try:
            rec = conn.recv(1024).decode(FORMAT)
            rec = json.loads(rec)
            print("client:", addr, "sends", rec)

            if not "file_name" in rec or not "local_name" in rec:
                conn.sendall("RESPONSE 404".encode(FORMAT))
                return False
            if not addr in self.clients:
                self.clients[addr] = {rec["file_name"]: rec["local_name"]}
            else:
                if rec["file_name"] in self.clients[addr]:
                    conn.sendall("RESPONSE 404".encode(FORMAT))
                    return False
                self.clients[addr][rec["file_name"]] = rec["local_name"]
            if rec["file_name"] not in self.file_names:
                self.file_names[rec["file_name"]] = [addr]
            else:
                self.file_names[rec["file_name"]].append(addr)
            conn.sendall("RESPONSE 200".encode(FORMAT))
            return False
        except:
            conn.sendall("RESPONSE 404".encode(FORMAT))
            return False

    def send_list_clients(self, conn, addr):
        try:
            conn.sendall("RESPONSE 200".encode(FORMAT))
        except:
            return True

        file_name = conn.recv(1024).decode(FORMAT)

        to_send = {}
        if file_name in self.file_names:
            to_send["availability"] = "yes"
            clients = []
            for host in self.file_names[file_name]:
                if not host in self.clients or not self.ping(host):
                    continue
                else:
                    self.discover(host)
                    if file_name in self.clients[host]:
                        clients.append(host)
            self.file_names[file_name] = clients
            if len(self.file_names[file_name]) == 0:
                self.file_names.pop(file_name)
            hash_names = []
            for cli in clients:
                hash_names.append((cli, self.clients[cli][file_name]))
            to_send["host_names"] = hash_names
        else:
            to_send["availability"] = "no"

        to_send = json.dumps(to_send)
        conn.sendall(to_send.encode(FORMAT))

        return False

    def ping(self, hostname):
        if not hostname in self.clients:
            return False
        try:
            temp_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            temp_soc.connect(hostname)
            temp_soc.sendall("PING".encode(FORMAT))

            rec = temp_soc.recv(1024).decode(FORMAT)
            print("client", hostname, "sends", rec)
            temp_soc.close()
            if rec == "RESPONSE 200":
                return True
            else:
                return False
        except:
            return False

    def discover(self, hostname):
        if not hostname in self.clients:
            return {}
        try:
            temp_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            temp_soc.connect(hostname)
            temp_soc.sendall("DISCOVER".encode(FORMAT))

            rec = temp_soc.recv(1024).decode(FORMAT)
            print("client", hostname, "sends", rec)

            if rec == "RESPONSE 200":
                dic = self.clients[hostname]
                dic = json.dumps(dic)

                temp_soc.sendall(dic.encode(FORMAT))
                dic = temp_soc.recv(1024).decode(FORMAT)
                self.clients[hostname] = json.loads(dic)
                return self.clients[hostname]
            else:
                return {}

        except:
            return {}

    def send_list(self, conn, addr):
        try:
            conn.sendall("RESPONSE 200".encode(FORMAT))
        except:
            return True
        rec = conn.recv(1024).decode(FORMAT)
        dic = self.file_names
        dic = json.dumps(dic)

        conn.sendall(dic.encode(FORMAT))
        return False

    def send_my_file(self, conn, addr):
        try:
            conn.sendall("RESPONSE 200".encode(FORMAT))
        except:
            return True
        rec = conn.recv(1024).decode(FORMAT)
        dic = self.clients[addr]
        dic = json.dumps(dic)

        conn.sendall(dic.encode(FORMAT))
        return False

    def delete_file(self, conn, addr):
        try:
            conn.sendall("RESPONSE 200".encode(FORMAT))
        except:
            return True
        file_name = conn.recv(1024).decode(FORMAT)
        self.clients[addr].pop(file_name)
        self.file_names[file_name].remove(addr)
        if len(self.file_names[file_name]) == 0:
            self.file_names.pop(file_name)
        conn.sendall("DELETED".encode(FORMAT))
        return False
