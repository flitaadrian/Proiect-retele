import socket
import time
from threading import Thread
from pathlib2 import Path
import os


buffer = None
mesaj = None
nume_fisier = ''
path = Path('./clientFile')


def threadFunction():
    global buffer, mesaj, server
    while True:
        try:
            if 'Actualizare' in buffer.decode("utf-8") and mesaj is None:
                print(buffer.decode("utf-8"))
                buffer = None
        except AttributeError:
            print()
        if buffer is None:
            buffer = server.recv(1024)
        if mesaj == "4":
            break


def threadAfisare():
    global buffer, mesaj, server, nume_fisier, path
    while True:
        if buffer:
            serverMesaj = buffer.decode("utf-8")
            if not mesaj:
                buffer = None
                print(serverMesaj)
            if '1 - lista fisiere' in serverMesaj:
                mesaj = input('')
                server.send(bytes(mesaj, "utf-8"))
                if mesaj == '4':
                    break
                buffer = None
                mesaj = None
            if 'Introduceti numele fisierului:' in serverMesaj:
                buffer = None
                mesaj = input('')
                server.send(bytes(mesaj, "utf-8"))
                while True:
                    if buffer:
                        serverFile = buffer
                        buffer = None
                        if 'Fisier nu exista' in serverFile.decode("utf-8"):
                            print(serverFile.decode("utf-8"))
                            mesaj = input('')
                            server.send(bytes(mesaj, "utf-8"))
                        else:
                            with open(path / mesaj, "wb") as file:
                                file.write(serverFile)
                                nume_fisier = mesaj
                            break
                mesaj = None
            elif 'Introduceti numele va rog' in serverMesaj:
                buffer = None
                mesaj = input('')
                server.send(bytes(mesaj, "utf-8"))
                mesaj = None
            elif 'Editare fisier' in serverMesaj:
                buffer = None
                mesaj = input('')
                server.send(bytes(mesaj, "utf-8"))
                if mesaj == '1':
                    os.remove(path / nume_fisier)
                elif mesaj == '2':
                    time.sleep(0.5)
                    with open(path / nume_fisier, "rb") as file:
                        data_file = file.read(1024)
                        server.send(data_file)
                mesaj = None
            elif 'Adaugati numele fisierului' in serverMesaj:
                buffer = None
                mesaj = input('')
                value = mesaj
                mesaj = None
                server.send(bytes(value, "utf-8"))
                while True:
                    if os.path.exists(path / value):
                        with open(path / value, 'rb') as file:
                            data_to_send = file.read(1024)
                            if not data_to_send:
                                server.send('Empty file'.encode())
                            else:
                                server.send(data_to_send)
                        break
                    elif value == '1':
                        server.send('Renuntare'.encode())
                        break
                    else:
                        print(', '. join(os.listdir(path)))
                        value = input('Acestea sunt fisierele existente care pot fi trimise, scrie numele unuia din lista\nsau\nscrie 1 pentru renuntare:')
            elif 'Fisierul exista deja pe disc' in serverMesaj:
                buffer = None
                mesaj = input('')
                server.send(bytes(mesaj, "utf-8"))
                mesaj = None


server = socket.socket()
host = '127.0.0.1'
port = 8080
server.connect((host, port))
print("Conectat")

p1 = Thread()
p1.__init__(target=threadFunction)
p1.start()

p2 = Thread()
p2.__init__(target=threadAfisare)
p2.start()

p2.join()
p1.join()
