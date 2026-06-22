import socket
import threading

HEADER = 64
PORT = 5050
SERVER = "0.0.0.0"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen()

clients = []
nicknames = []


def remove_client(client):
    index = clients.index(client)
    client.close()
    print(clients)
    nickname = nicknames[index]
    clients.remove(client)
    print(f"{nickname} desconectou do chat")
    broadcast(f"{nickname} left the chat".encode(FORMAT))
    nicknames.remove(nickname)


def broadcast(message):
    for client in clients:
        client.send(message)


def handle_client(client, addr):
    connected = True
    while connected:
        try:
            msg_length = client.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = client.recv(msg_length).decode(FORMAT)
                if msg == DISCONNECT_MESSAGE:
                    remove_client(client)
                    break
                broadcast(msg.encode(FORMAT))

        except:
            remove_client(client)
            break
    client.close()


def receive():
    while True:
        client, addr = server.accept()
        print(f"Connected with {str(addr)}")

        client.send("NICK".encode(FORMAT))
        nickname = client.recv(1024).decode(FORMAT)
        nicknames.append(nickname)
        clients.append(client)

        print(f"Nickname of client is {nickname}")
        broadcast(f"{nickname} joined the chat".encode(FORMAT))
        client.send("Connected to the server".encode(FORMAT))

        thread = threading.Thread(target=handle_client, args=(client, addr))
        thread.start()


print("[STARTING] server is listening...")
receive()
