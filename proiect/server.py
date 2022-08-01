import datetime
import os
import socket
import time
from threading import Thread
from pathlib2 import Path

lista_fisiere = []

path = Path('./serverData')


def getFisiere():
    global lista_fisiere, path
    fisiere = os.listdir(path)
    for fisier in fisiere:
        vector = [fisier, []]
        lista_fisiere.append(vector)


def sendFisiere(nume_client, client):
    global path
    data = 'Introduceti numele fisierului: '.encode()
    client.send(data)
    nume_fisier = client.recv(1024).decode("utf-8")
    while True:
        for fisier in lista_fisiere:
            if nume_fisier in fisier[0]:
                file = open(path / fisier[0], "rb")
                date_fisier = file.read(1024)
                fisier[1].append(nume_client)
                print("Datele au fost transmise cu succes")
                return date_fisier, nume_fisier
        data = 'Fisier nu exista, alegeti altul din lista urmatoare\n{}\n'.format(', '.join(os.listdir(path))).encode()
        client.send(data)
        nume_fisier = client.recv(1024).decode("utf-8")


def sendListFisiere():
    data = '\nFisiere:\n'
    for fisier in lista_fisiere:
        data += fisier[0] + ', detinut in editare de: {}\n'.format(', '.join(fisier[1]))
    return data


def editareFile(client, nume_fisier, nume_client):
    global path, lista_fisiere
    data = 'Editare fisier\nPoti alege:\n1 - Renuntare editare fisier\n2 - Push fisier updated\n3 - Stergere fisier'
    client.send(data.encode())
    while True:
        comanda = client.recv(1024).decode("utf-8")
        print(comanda)
        if '1' in comanda:
            for fisier in lista_fisiere:
                if nume_fisier in fisier[0]:
                    fisier[1].remove(nume_client)
                    print("Datele au fost actualizate cu succes")
            client.send('Editare inchisa!'.encode())
            break
        elif '2' in comanda:
            fisier_actualizat = client.recv(1024)
            with open(path / nume_fisier, 'wb') as file:
                file.write(fisier_actualizat)
            client.send('Actualizare reusita!'.encode())
            for fisier in lista_fisiere:
                if nume_fisier in fisier[0]:
                    fisier[1].remove(nume_client)
                    print("Datele au fost actualizate cu succes")
            break
        elif '3' in comanda:
            os.remove(path / nume_fisier)
            for fisier in lista_fisiere:
                if nume_fisier in fisier[0]:
                    fisier.clear()
                    print("Datele au fost actualizate cu succes")
            lista_fisiere = [fisier for fisier in lista_fisiere if fisier != []]
            break
        else:
            client.send('Nu exista comanda\n{}'.format(data).encode())


def functie(client, address):
    data = 'Introduceti numele va rog: '.encode()
    client.send(data)
    nume_client = client.recv(1024).decode("utf-8")
    nume_clienti.append(nume_client)
    clienti.append(client)
    try:
        while True:
                comenzi = '1 - lista fisiere\n2 - cerere fisier\n3 - adaugare fisier\n4 - inchide programul\n'.encode()
                client.send(comenzi)
                comanda = client.recv(1024).decode("utf-8")
                print(comanda)
                if comanda == '1':
                    fisierele = sendListFisiere()
                    client.send(fisierele.encode())
                elif comanda == '2':
                    data_file, nume_fisier = sendFisiere(nume_client, client)
                    if not data_file:
                        client.send('Empty file'.encode())
                    else:
                        client.send(data_file)
                    fisierele = '\nActualizare:{}\n'.format(sendListFisiere())
                    for user in clienti:
                        user.send(fisierele.encode())

                    editareFile(client, nume_fisier, nume_client)

                    fisierele_actualizate = '\nActualizare pe fisierul: {}'.format(nume_fisier)
                    fisierele = '\nActualizare:{}\n'.format(sendListFisiere())
                    for user in clienti:
                        user.send((fisierele_actualizate + '\n' + fisierele).encode())
                elif comanda == '3':
                    data = 'Adaugati numele fisierului: '.encode()
                    client.send(data)
                    nume_fisier = client.recv(1024).decode("utf-8")
                    data_recieved = client.recv(1024)
                    if data_recieved.decode() != 'Renuntare':
                        ok = 1
                        for fisier in lista_fisiere:
                            if nume_fisier in fisier[0]:
                                ok = 0
                        if ok:
                            mesaj = 0
                            with open(path / nume_fisier, 'wb') as file:
                                file.write(data_recieved)
                            lista_fisiere.append([nume_fisier, []])
                        else:
                            data = 'Fisierul exista deja pe disc, doriti sa il actualizati?\n1 - renuntare\n2 - actualizare'
                            client.send(data.encode())
                            ok = 1
                            while True:
                                mesaj = client.recv(1024).decode("utf-8")
                                if mesaj == '1':
                                    ok = 0
                                    break
                                elif mesaj == '2':
                                    with open(path / nume_fisier, 'wb') as file:
                                        file.write(data_recieved)
                                    client.send('Actualizare reusita!'.encode())
                                    print("Datele au fost actualizate cu succes")
                                    break
                                else:
                                    client.send(('Comanda nu exista\n' + data).encode())
                        if ok:
                            if mesaj == '2':
                                fisierele_actualizate = '\nActualizare, fisier actualizat: {}'.format(nume_fisier)
                            else:
                                fisierele_actualizate = '\nActualizare, fisier adaugat: {}'.format(nume_fisier)
                            fisierele = '\nActualizare:{}\n'.format(sendListFisiere())
                            for user in clienti:
                                try:
                                    user.send((fisierele_actualizate + fisierele).encode())
                                except ConnectionResetError:
                                    continue
                elif comanda == '4':
                    client.send('Exit'.encode())
                    break
                else:
                    client.send('Nu exista comanda'.encode())
        client.close()
    except ConnectionAbortedError:
        client.close()
        try:
            clienti.remove(client)
        except ValueError:
            print()
    except ConnectionResetError:
        for fisier in lista_fisiere:
            if nume_client in fisier[1]:
                try:
                    fisier[1].remove(nume_client)
                except ValueError:
                    ok = 0
        client.close()
        try:
            clienti.remove(client)
        except ValueError:
            print()


server = socket.socket()
host = '127.0.0.1'
port = 8080
server.bind((host, port))
server.listen(5)
clienti = []
nume_clienti = []
getFisiere()

while True:
    client2, address2 = server.accept()
    print(f"Conexiune stabilita - {address2[0]}:{address2[1]}")

    p1 = Thread()
    p1.__init__(target=functie, args=(client2, address2))
    p1.start()

